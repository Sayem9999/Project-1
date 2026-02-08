import { cn } from '@/lib/utils';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    icon?: React.ReactNode;
}

export function Input({ className, label, icon, ...props }: InputProps) {
    return (
        <div className="space-y-2">
            {label && <label className="text-sm font-medium text-gray-400 ml-1">{label}</label>}
            <div className="relative group">
                {icon && (
                    <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-brand-cyan transition-colors">
                        {icon}
                    </div>
                )}
                <input
                    className={cn(
                        "w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-gray-600 focus:outline-none focus:ring-2 focus:ring-brand-cyan/50 focus:border-transparent transition-all",
                        icon && "pl-10",
                        className
                    )}
                    {...props}
                />
            </div>
        </div>
    );
}
