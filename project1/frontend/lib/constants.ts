type NodeTypeOption = {
  value: string;
  label: string;
};

type SectorOption = {
  value: string;
  label: string;
  sampleLabel?: string;
};

export const NODE_TYPE_OPTIONS: readonly NodeTypeOption[] = [
  { value: 'company', label: 'Company' },
  { value: 'person', label: 'Person' },
  { value: 'project', label: 'Project' },
  { value: 'organization', label: 'Organization' },
] as const;

export const SECTOR_OPTIONS: readonly SectorOption[] = [
  { value: 'ai', label: 'Artificial Intelligence', sampleLabel: 'AI' },
  { value: 'automotive', label: 'Automotive' },
  { value: 'consumer', label: 'Consumer' },
  { value: 'enterprise', label: 'Enterprise' },
  { value: 'cloud', label: 'Cloud' },
  { value: 'semiconductors', label: 'Semiconductors' },
  { value: 'finance', label: 'Finance' },
  { value: 'healthcare', label: 'Healthcare' },
  { value: 'energy', label: 'Energy' },
  { value: 'industrial', label: 'Industrial' },
] as const;

export const SECTOR_SAMPLE_LABELS = SECTOR_OPTIONS.map((option) => option.sampleLabel ?? option.label);

