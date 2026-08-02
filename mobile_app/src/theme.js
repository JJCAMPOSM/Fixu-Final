export const colors = {
  primary: '#4f46e5',
  primaryDark: '#4338ca',
  background: '#f3f4f6',
  surface: '#ffffff',
  text: '#111827',
  textMuted: '#6b7280',
  border: '#e5e7eb',
  danger: '#dc2626',
  dangerBg: '#fee2e2',
  success: '#16a34a',
  successBg: '#dcfce7',
  warning: '#d97706',
  warningBg: '#fef3c7',
  info: '#2563eb',
  infoBg: '#dbeafe',
};

export const STATUS_STYLE = {
  open: { label: 'Abierto', bg: colors.infoBg, fg: colors.info },
  pending: { label: 'Pendiente', bg: colors.warningBg, fg: colors.warning },
  solved: { label: 'Resuelto', bg: colors.successBg, fg: colors.success },
  closed: { label: 'Cerrado', bg: colors.border, fg: colors.textMuted },
};

export const PRIORITY_STYLE = {
  low: { label: 'Baja', bg: colors.successBg, fg: colors.success },
  medium: { label: 'Media', bg: colors.warningBg, fg: colors.warning },
  high: { label: 'Alta', bg: colors.dangerBg, fg: colors.danger },
};
