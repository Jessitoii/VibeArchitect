import React from 'react';
import { useStore } from '../store';
import { CheckCircle, XCircle, FileText } from 'lucide-react';

export default function ReviewAndDeploy({ onApprove }: { onApprove: () => void }) {
    const { manifest } = useStore();

    // Check if Auditor had issues
    const auditLog = manifest?.audit_log || [];
    const hasCritical = auditLog.some((a: any) => a.severity === "critical");

    return (
        <div className="absolute inset-0 z-[150] bg-background/95 backdrop-blur-xl flex justify-center items-center p-8">
            <div className="bg-surface border border-border rounded-xl shadow-2xl w-full max-w-5xl max-h-full flex flex-col">
                <div className="p-8 border-b border-border space-y-2">
                    <h2 className="text-4xl font-black flex items-center gap-3">
                        Review &amp; Deploy
                        {hasCritical ? <XCircle className="text-error" size={32} /> : <CheckCircle className="text-success" size={32} />}
                    </h2>
                    <p className="text-text-dim/80 text-lg font-medium">Auditor phase complete. Review findings and the generated assets before scaffolding to disk.</p>
                </div>

                <div className="p-8 flex-1 overflow-hidden flex gap-8">
                    {/* Findings */}
                    <div className="flex-1 space-y-4 flex flex-col overflow-hidden">
                        <h3 className="font-bold text-xl text-primary">Auditor Findings</h3>
                        <div className="flex-1 overflow-auto rounded-lg border border-border/50 bg-background/50 p-2">
                            {auditLog.length === 0 ? (
                                <div className="text-success text-sm bg-success/10 p-4 rounded-lg font-bold border border-success/20">✅ No issues found. Architecture is solid.</div>
                            ) : (
                                <ul className="space-y-3">
                                    {auditLog.map((log: any, i: number) => (
                                        <li key={i} className={`p-4 rounded-lg text-sm border ${log.severity === "critical" ? "bg-error/10 text-error border-error/20" :
                                                log.severity === "warning" ? "bg-accent/10 text-accent border-accent/20" :
                                                    "bg-secondary/10 text-secondary border-secondary/20"
                                            }`}>
                                            <span className="font-bold uppercase tracking-widest text-[10px] block opacity-70 mb-2">{log.severity}</span>
                                            {log.message}
                                        </li>
                                    ))}
                                </ul>
                            )}
                        </div>
                    </div>

                    {/* Files Preview */}
                    <div className="flex-1 space-y-4 flex flex-col overflow-hidden">
                        <h3 className="font-bold text-xl text-secondary">Generated Files Overview</h3>
                        <div className="flex-1 bg-background/50 border border-border/50 rounded-lg p-6 text-sm font-mono overflow-auto space-y-3">
                            <div className="flex items-center gap-3 text-text font-bold"><FileText size={16} className="text-primary" /> GEMINI.md</div>
                            {manifest?.instructional_brain?.context_md && <div className="flex items-center gap-3 text-text font-bold"><FileText size={16} className="text-accent" /> CONTEXT.md</div>}
                            <div className="flex items-center gap-3 text-text font-bold"><FileText size={16} className="text-secondary" /> metadata.json</div>

                            <div className="pl-6 border-l-2 border-border/30 ml-2 space-y-3 mt-4">
                                <div className="text-text-dim/70 uppercase tracking-widest text-[10px] font-bold mt-4">/rules</div>
                                {manifest?.instructional_brain?.rules?.map((r: any, i: number) => (
                                    <div key={i} className="pl-4 text-text/90 flex items-center gap-2"><FileText size={14} className="opacity-50" /> {r.filename}</div>
                                ))}

                                <div className="text-text-dim/70 uppercase tracking-widest text-[10px] font-bold mt-4">/workflows</div>
                                {manifest?.instructional_brain?.workflows?.map((w: any, i: number) => (
                                    <div key={i} className="pl-4 text-text/90 flex items-center gap-2"><FileText size={14} className="opacity-50" /> {w.filename}</div>
                                ))}

                                <div className="text-text-dim/70 uppercase tracking-widest text-[10px] font-bold mt-4">/docs</div>
                                {manifest?.instructional_brain?.docs?.map((d: any, i: number) => (
                                    <div key={i} className="pl-4 text-text/90 flex items-center gap-2"><FileText size={14} className="opacity-50" /> {d.filename}</div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                <div className="p-8 border-t border-border flex justify-end gap-4 bg-surface/50">
                    <button
                        onClick={onApprove}
                        className="px-10 py-4 bg-primary hover:bg-primary/80 font-black tracking-widest uppercase text-white rounded-xl shadow-xl shadow-primary/20 transition-all hover:scale-105 active:scale-95"
                    >
                        Approve &amp; Scaffold
                    </button>
                </div>
            </div>
        </div>
    );
}
