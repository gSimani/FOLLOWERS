export type Note = "A" | "A#" | "B" | "C" | "C#" | "D" | "D#" | "E" | "F" | "F#" | "G" | "G#"
export type StringNote = "E" | "A" | "D" | "G" | "B"

export interface FretboardNote {
  note: Note
  isSharp: boolean
  isHighlighted: boolean
  isChordTone: boolean
}

export interface ChordPosition {
  position: number
  frets: (string | null)[]
  isValid: boolean
}

