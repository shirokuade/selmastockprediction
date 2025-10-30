import { ReactNode } from 'react';
import { cn } from '@/lib/utils';
import { AlertCircle, CheckCircle, Info, XCircle } from 'lucide-react';

interface AlertProps {
  children: ReactNode;
  variant?: 'info' | 'success' | 'warning' | 'error';
  className?: string;
}

export default function Alert({ children, variant = 'info', className }: AlertProps) {
  const variants = {
    info: {
      container: 'bg-blue-50 border-blue-200 text-blue-800',
      icon: Info,
    },
    success: {
      container: 'bg-green-50 border-green-200 text-green-800',
      icon: CheckCircle,
    },
    warning: {
      container: 'bg-yellow-50 border-yellow-200 text-yellow-800',
      icon: AlertCircle,
    },
    error: {
      container: 'bg-red-50 border-red-200 text-red-800',
      icon: XCircle,
    },
  };

  const { container, icon: Icon } = variants[variant];

  return (
    <div className={cn('border rounded-lg p-4 flex items-start gap-3', container, className)}>
      <Icon className="h-5 w-5 flex-shrink-0 mt-0.5" />
      <div className="flex-1">{children}</div>
    </div>
  );
}
