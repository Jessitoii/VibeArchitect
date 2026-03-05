import React from "react";
import { motion } from "framer-motion";
import { CheckCircle2, Circle, Loader2, AlertCircle, RotateCcw } from "lucide-react";

interface StepProps {
    id: string;
    label: string;
    status: "pending" | "current" | "completed" | "error" | "rollback";
}

const steps: StepProps[] = [
    { id: "VISIONARY", label: "Visionary", status: "pending" },
    { id: "ARCHITECT", label: "Architect", status: "pending" },
    { id: "ENGINEER", label: "Engineer", status: "pending" },
    { id: "EXPERT", label: "Expert", status: "pending" },
    { id: "AUDITOR", label: "Auditor", status: "pending" },
];

const PipelineStepper: React.FC<{ currentId: string | null; status: string }> = ({ currentId, status }) => {
    const getStepStatus = (stepId: string, index: number) => {
        const currentIndex = steps.findIndex(s => s.id === currentId);
        if (currentIndex === -1) return "pending";

        if (index < currentIndex) return "completed";
        if (index === currentIndex) {
            if (status === "error") return "error";
            if (status === "rollback") return "rollback";
            return "current";
        }
        return "pending";
    };

    return (
        <div className="w-full h-24 flex items-center justify-between px-12 bg-surface/30 backdrop-blur-md border-b border-border shadow-inner">
            {steps.map((step, index) => {
                const stepStatus = getStepStatus(step.id, index);
                const isActive = stepStatus === "current" || stepStatus === "error" || stepStatus === "rollback";

                return (
                    <React.Fragment key={step.id}>
                        <div className="flex flex-col items-center relative z-10">
                            <motion.div
                                initial={false}
                                animate={{
                                    scale: isActive ? 1.2 : 1,
                                    backgroundColor: stepStatus === "completed" ? "#10b981" : isActive ? (stepStatus === "error" ? "#ef4444" : stepStatus === "rollback" ? "#f59e0b" : "#6366f1") : "#2a2e37",
                                }}
                                className="w-10 h-10 rounded-full flex items-center justify-center text-white shadow-xl"
                            >
                                {stepStatus === "completed" ? <CheckCircle2 size={24} /> :
                                    stepStatus === "error" ? <AlertCircle size={24} /> :
                                        stepStatus === "rollback" ? <RotateCcw size={24} /> :
                                            isActive ? <Loader2 size={24} className="animate-spin" /> :
                                                <Circle size={24} className="opacity-30" />}
                            </motion.div>
                            <span className={`mt-3 text-[10px] font-bold uppercase tracking-widest ${isActive ? 'text-accent' : 'text-text-dim'}`}>
                                {step.label}
                            </span>
                        </div>

                        {index < steps.length - 1 && (
                            <div className="flex-1 h-[2px] mx-4 bg-border relative">
                                <motion.div
                                    initial={{ width: "0%" }}
                                    animate={{ width: stepStatus === "completed" ? "100%" : "0%" }}
                                    transition={{ duration: 0.8, ease: "easeInOut" }}
                                    className="absolute inset-0 bg-primary shadow-[0_0_15px_rgba(223,145,42,0.4)]"
                                />
                            </div>
                        )}
                    </React.Fragment>
                );
            })}
        </div>
    );
};

export default PipelineStepper;
