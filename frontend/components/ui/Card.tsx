import { motion } from 'framer-motion';
import { cn } from '@/lib/utils'; // Assuming utils exists, if not I'll inline or create it

export function Card({ children, className, gradient = false }: { children: React.ReactNode; className?: string; gradient?: boolean }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className={cn(
                "rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-6 relative overflow-hidden group",
                gradient && "bg-gradient-to-br from-white/5 to-transparent",
                className
            )}
        >
            {gradient && (
                <div className="absolute inset-0 bg-gradient-to-r from-brand-cyan/10 to-brand-violet/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            )}
            <div className="relative z-10">{children}</div>
        </motion.div>
    );
}
