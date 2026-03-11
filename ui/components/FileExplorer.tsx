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
            // ── .agent/ virtual node ──────────────────────────────────────
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

                // New schema: AGENT.md + RULES.md + metadata.json
                if (brain.agent_md) agentNode.children!.push({ name: 'AGENT.md', isDirectory: false, path: `${agentNode.path}/AGENT.md` });
                if (brain.rules_md) agentNode.children!.push({ name: 'RULES.md', isDirectory: false, path: `${agentNode.path}/RULES.md` });
                if (brain.metadata_index?.length || brain.metadata_json) agentNode.children!.push({ name: 'metadata.json', isDirectory: false, path: `${agentNode.path}/metadata.json` });

                // rules/ folder: auto_*.md + sub_agents/ subdirectory
                if ((brain.rules && brain.rules.length > 0) || (brain.sub_agent_rules && brain.sub_agent_rules.length > 0)) {
                    const rulesFolder: FileNode = { name: 'rules', isDirectory: true, path: `${agentNode.path}/rules`, children: [] };

                    // Auto-generated preventative rules
                    (brain.rules || []).forEach((r: any) => {
                        if (r.filename) rulesFolder.children!.push({ name: r.filename, isDirectory: false, path: `${rulesFolder.path}/${r.filename}` });
                    });

                    // Sub-agent domain rulebooks inside rules/sub_agents/
                    if (brain.sub_agent_rules && brain.sub_agent_rules.length > 0) {
                        const subAgentsFolder: FileNode = { name: 'sub_agents', isDirectory: true, path: `${rulesFolder.path}/sub_agents`, children: [] };
                        brain.sub_agent_rules.forEach((sar: any) => {
                            if (sar.filename) subAgentsFolder.children!.push({ name: sar.filename, isDirectory: false, path: `${subAgentsFolder.path}/${sar.filename}` });
                        });
                        rulesFolder.children!.push(subAgentsFolder);
                    }

                    agentNode.children!.push(rulesFolder);
                }
                addVirtualNode('workflows', brain.workflows);
                // Skills may be in Claude-style subdirs (skill-name/SKILL.md)
                if (brain.skills && brain.skills.length > 0) {
                    const skillsFolder: FileNode = { name: 'skills', isDirectory: true, path: `${agentNode.path}/skills`, children: [] };
                    const skillDirs: Record<string, FileNode> = {};
                    brain.skills.forEach((s: any) => {
                        if (!s.filename) return;
                        if (s.filename.includes('/')) {
                            const [dirName, fileName] = s.filename.split('/');
                            if (!skillDirs[dirName]) {
                                skillDirs[dirName] = { name: dirName, isDirectory: true, path: `${skillsFolder.path}/${dirName}`, children: [] };
                                skillsFolder.children!.push(skillDirs[dirName]);
                            }
                            skillDirs[dirName].children!.push({ name: fileName, isDirectory: false, path: `${skillsFolder.path}/${s.filename}` });
                        } else {
                            skillsFolder.children!.push({ name: s.filename, isDirectory: false, path: `${skillsFolder.path}/${s.filename}` });
                        }
                    });
                    agentNode.children!.push(skillsFolder);
                }
                // NOTE: docs go to /docs/ at project root (see below)

                entries = [agentNode, ...entries];
            }

            // ── /docs/ virtual node at project root ───────────────────────
            const hasDocs = entries.some(e => e.name === 'docs' && e.isDirectory);
            if (!hasDocs && brain.docs && brain.docs.length > 0) {
                const docsRoot: FileNode = { name: 'docs', isDirectory: true, path: `${projectPath}/docs`, children: [] };
                const subFolders: Record<string, FileNode> = {};

                brain.docs.forEach((doc: any) => {
                    if (!doc.filename) return;
                    const parts = doc.filename.split('/');
                    if (parts.length > 1) {
                        // e.g. "ui/Dashboard.md" → subfolder "ui"
                        const sub = parts[0];
                        if (!subFolders[sub]) {
                            subFolders[sub] = { name: sub, isDirectory: true, path: `${docsRoot.path}/${sub}`, children: [] };
                            docsRoot.children!.push(subFolders[sub]);
                        }
                        subFolders[sub].children!.push({ name: parts[1], isDirectory: false, path: `${docsRoot.path}/${doc.filename}` });
                    } else {
                        docsRoot.children!.push({ name: doc.filename, isDirectory: false, path: `${docsRoot.path}/${doc.filename}` });
                    }
                });

                entries = [...entries, docsRoot];
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

        // If file physically doesn't exist yet but is in manifest (virtual preview)
        if (!content && (path.includes('.agent') || path.includes('/docs/'))) {
            const brain = manifest?.instructional_brain;
            if (brain) {
                if (path.endsWith('AGENT.md')) content = brain.agent_md;
                else if (path.endsWith('RULES.md')) content = brain.rules_md;
                else if (path.endsWith('metadata.json')) {
                    // Build metadata.json preview from metadata_index
                    const idx = brain.metadata_index?.length
                        ? brain.metadata_index
                        : brain.metadata_json;
                    content = JSON.stringify({ schema_version: 2, index: idx }, null, 2);
                } else {
                    const folderName = path.split('/').slice(-2, -1)[0];
                    const fileName = path.split('/').pop();
                    // Resolve from skills/rules/workflows subfolder lists
                    const listSources: Record<string, any[]> = {
                        rules: brain.rules || [],
                        workflows: brain.workflows || [],
                        skills: brain.skills || [],
                    };
                    if (folderName && listSources[folderName]) {
                        const found = listSources[folderName].find((f: any) => f.filename === fileName);
                        if (found) content = found.content;
                    }
                    // Sub-agent rulebooks: path ends in rules/sub_agents/{filename}
                    if (!content && brain.sub_agent_rules && path.includes('sub_agents')) {
                        const found = brain.sub_agent_rules.find((s: any) => path.endsWith(s.filename));
                        if (found) content = found.content;
                    }
                    // For /docs/ virtual files, resolve by filename (may include sub-path)
                    if (!content && brain.docs) {
                        const relativePath = path.includes('/docs/') ? path.split('/docs/').pop() : null;
                        if (relativePath) {
                            const found = brain.docs.find((d: any) => d.filename === relativePath);
                            if (found) content = found.content;
                        }
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
