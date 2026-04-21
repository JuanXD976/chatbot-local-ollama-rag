"use client";

type Props = {
  mode: string;
  outputFormat: string;
  onModeChange: (value: string) => void;
  onOutputFormatChange: (value: string) => void;
};

export default function ModeSelector({
  mode,
  outputFormat,
  onModeChange,
  onOutputFormatChange,
}: Props) {
  return (
    <div className="mode-selector">
      <select className="btn mode-select" value={mode} onChange={(e) => onModeChange(e.target.value)}>
        <option value="auto">Modo: Auto</option>
        <option value="analista">Modo: Analista</option>
        <option value="programador">Modo: Programador</option>
        <option value="resumidor">Modo: Resumidor</option>
      </select>

      <select className="btn mode-select" value={outputFormat} onChange={(e) => onOutputFormatChange(e.target.value)}>
        <option value="normal">Salida: Normal</option>
        <option value="puntos">Salida: Puntos</option>
        <option value="tabla">Salida: Tabla</option>
        <option value="codigo">Salida: Código</option>
      </select>
    </div>
  );
}