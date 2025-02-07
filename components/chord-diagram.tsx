interface ChordDiagramProps {
  position: number
  frets: (string | null)[]
  isValid: boolean
  stringLabels: string[]
}

export function ChordDiagram({ position, frets, isValid, stringLabels }: ChordDiagramProps) {
  return (
    <div className="flex flex-col items-center gap-4">
      <h2 className={`text-xl font-semibold ${!isValid ? "text-red-500" : ""}`}>
        Position {position} {!isValid && "(Invalid)"}
      </h2>

      <div className="grid grid-cols-6 gap-4">
        {stringLabels.map((label, i) => (
          <div key={i} className="flex flex-col items-center gap-2">
            <span className="text-sm font-medium">{label}</span>
            <span className={`text-lg font-bold ${frets[i] === "x" ? "text-red-500" : "text-blue-600"}`}>
              {frets[i]}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

