import React, { useEffect, useState, useRef } from 'react';
import { useStore } from '../store';
import { ChevronRight, ChevronDown, File, Folder } from 'lucide-react';

interface FileNode {
    name: string;
    isDirectory: boolean;
    path: string;
    children?: FileNode[];
    isOpen?: boolean;
}

const TreeNode = ({ node, level, onToggle, onSelect }: { node: FileNode, level: number, onToggle: (path: string) => void, onSelect: (path: string) => void }) => {
    const { activeFilePath } = useStore();
    const isActive = activeFilePath === node.path;

    return (
        <div>
            <div
                className={`flex items-center gap-2 py-1 px-2 cursor-pointer hover:bg-surface/50 text-sm ${isActive ? 'bg-primary/20 text-primary font-medium' : 'text-text-dim'}`}
                style={{ paddingLeft: `${level * 12 + 8}px` }}
                onClick={() => node.isDirectory ? onToggle(node.path) : onSelect(node.path)}
            >
                {node.isDirectory ? (
                    node.isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />
                ) : (
                    <File size={14} className="opacity-50 ml-4" />
                )}

                {node.isDirectory && <Folder size={14} className="text-secondary" />}
                <span className="truncate">{node.name}</span>
            </div>

            {node.isDirectory && node.isOpen && node.children && (
                <div>
                    {node.children.map((child) => (
                        <TreeNode key={child.path} node={child} level={level + 1} onToggle={onToggle} onSelect={onSelect} />
                    ))}
                </div>
            )}
        </div>
    );
};

export default function FileExplorer() {
    const { projectPath, setActiveFile, manifest } = useStore();
    const [tree, setTree] = useState<FileNode[]>([]);

    // Quick local state for toggled folders
    const [expandedPaths, setExpandedPaths] = useState<Set<string>>(new Set());
    const expandedPathsRef = useRef<Set<string>>(new Set());

    useEffect(() => {
        if (projectPath) {
            loadRoot();
            window.electronAPI.watchDir(projectPath);
            const cleanup = window.electronAPI.onFileChanged(() => {
                refreshTree();
            });
            return cleanup;
        }
    }, [projectPath]);

    const buildVirtualTree = (physicalEntries: FileNode[]): FileNode[] => {
        let entries = [...physicalEntries];
        const brain = manifest?.instructional_brain;

        if (brain) {
            const hasAgent = entries.some(e => e.name === '.agent' && e.isDirectory);
            if (!hasAgent) {
                const agentNode: FileNode = { name: '.agent', isDirectory: true, path: `${projectPath}/.agent`, children: [] };

                const addVirtualNode = (folder: string, files: any[]) => {
                    if (files && files.length > 0) {
                        const folderNode: FileNode = { name: folder, isDirectory: true, path: `${agentNode.path}/${folder}`, children: [] };
                        files.forEach((f: any) => {
                            if (f.filename) {
                                folderNode.children!.push({ name: f.filename, isDirectory: false, path: `${folderNode.path}/${f.filename}` });
                            }
                        });
                        agentNode.children!.push(folderNode);
                    }
                };

                if (brain.gemini_md) agentNode.children!.push({ name: 'GEMINI.md', isDirectory: false, path: `${agentNode.path}/GEMINI.md` });
                if (brain.context_md) agentNode.children!.push({ name: 'CONTEXT.md', isDirectory: false, path: `${agentNode.path}/CONTEXT.md` });
                if (brain.metadata_json) agentNode.children!.push({ name: 'metadata.json', isDirectory: false, path: `${agentNode.path}/metadata.json` });

                addVirtualNode('rules', brain.rules);
                addVirtualNode('workflows', brain.workflows);
                addVirtualNode('docs', brain.docs);
                addVirtualNode('skills', brain.skills);

                entries = [agentNode, ...entries];
            }
        }
        return entries;
    };

    const refreshTree = async () => {
        if (!projectPath) return;
        let rootEntries = await window.electronAPI.readDir(projectPath);
        rootEntries = buildVirtualTree(rootEntries);

        const expandNode = async (nodes: FileNode[]): Promise<FileNode[]> => {
            const currentExpanded = expandedPathsRef.current;
            return Promise.all(nodes.map(async node => {
                if (currentExpanded.has(node.path)) {
                    const children = await window.electronAPI.readDir(node.path);
                    return { ...node, children: await expandNode(children) };
                }
                return node;
            }));
        };

        setTree(await expandNode(rootEntries));
    };

    const loadRoot = async () => {
        if (!projectPath) return;
        let entries = await window.electronAPI.readDir(projectPath);
        entries = buildVirtualTree(entries);

        setTree(entries);

        // Auto-expand .agent if it exists or is virtual
        const agentDir = entries.find(e => e.name === '.agent' && e.isDirectory);
        if (agentDir) {
            handleToggle(agentDir.path);
        }
    };

    const handleToggle = async (path: string) => {
        const isExpanded = expandedPathsRef.current.has(path);

        const newExpanded = new Set(expandedPathsRef.current);
        if (isExpanded) {
            newExpanded.delete(path);
        } else {
            newExpanded.add(path);
        }

        expandedPathsRef.current = newExpanded;
        setExpandedPaths(newExpanded);

        if (!isExpanded) {
            // First try reading physically
            let children = await window.electronAPI.readDir(path);

            // If empty, check if it's a virtual folder we need to populate
            if (children.length === 0 && path.includes('.agent')) {
                const brain = manifest?.instructional_brain;
                if (brain) {
                    const folderName = path.split('/').pop();
                    // Define valid keys for file lists in InstructionalBrain
                    type FileListKey = 'rules' | 'workflows' | 'docs' | 'skills';
                    const validFileListKeys: FileListKey[] = ['rules', 'workflows', 'docs', 'skills'];

                    if (folderName && validFileListKeys.includes(folderName as FileListKey)) {
                        const files = brain[folderName as FileListKey] || [];
                        children = files.map((f: any) => ({
                            name: f.filename,
                            isDirectory: false,
                            path: `${path}/${f.filename}`
                        }));
                    }
                }
            }

            setTree(prev => insertChildren(prev, path, children));
        }
    };

    const insertChildren = (nodes: FileNode[], targetPath: string, children: FileNode[]): FileNode[] => {
        return nodes.map(node => {
            if (node.path === targetPath) {
                return { ...node, children };
            }
            if (node.children) {
                return { ...node, children: insertChildren(node.children, targetPath, children) };
            }
            return node;
        });
    };

    const handleSelect = async (path: string) => {
        let content = await window.electronAPI.readFile(path);

        // If file physically doesn't exist yet but is in manifest
        if (!content && path.includes('.agent')) {
            const brain = manifest?.instructional_brain;
            if (brain) {
                if (path.endsWith('GEMINI.md')) content = brain.gemini_md;
                else if (path.endsWith('CONTEXT.md')) content = brain.context_md;
                else if (path.endsWith('metadata.json')) content = JSON.stringify(brain.metadata_json, null, 2);
                else {
                    const folderName = path.split('/').slice(-2, -1)[0];
                    const fileName = path.split('/').pop();
                    if (folderName) {
                        const list = (brain as any)[folderName] || [];
                        const found = list.find((f: any) => f.filename === fileName);
                        if (found) content = found.content;
                    }
                }
            }
            if (!content) content = "// This file is currently being drafted by the AI...";
        }

        setActiveFile(path, content || "");
    };

    // Attach isOpen state dynamically
    const renderNode = (node: FileNode) => {
        const enrichedNode = { ...node, isOpen: expandedPaths.has(node.path) };
        if (enrichedNode.children) {
            enrichedNode.children = enrichedNode.children.map(c => ({ ...c, isOpen: expandedPaths.has(c.path) }));
        }
        return enrichedNode;
    };

    return (
        <div className="flex flex-col h-full bg-background border-r border-border min-w-[250px] w-[250px] overflow-hidden">
            <div className="p-4 border-b border-border">
                <h3 className="text-xs font-black uppercase tracking-widest text-text-dim">Explorer</h3>
            </div>
            <div className="flex-1 overflow-auto py-2">
                {tree.map(node => (
                    <TreeNode
                        key={node.path}
                        node={renderNode(node)}
                        level={0}
                        onToggle={handleToggle}
                        onSelect={handleSelect}
                    />
                ))}
            </div>
        </div>
    );
}
