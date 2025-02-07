import type { Note, FretboardNote, ChordPosition } from "@/types"

const NOTES: Note[] = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]

export const SCALES = {
  Major: [0, 2, 4, 5, 7, 9, 11],
  Minor: [0, 2, 3, 5, 7, 8, 10],
  "Harmonic Minor": [0, 2, 3, 5, 7, 8, 11],
  "Melodic Minor": [0, 2, 3, 5, 7, 9, 11],
  "Pentatonic Major": [0, 2, 4, 7, 9],
  "Pentatonic Minor": [0, 3, 5, 7, 10],
} as const

export const STANDARD_TUNING = ["E", "A", "D", "G", "B", "E"]

const CHORD_SHAPES = {
  major: ["x", "0", "2", "2", "2", "0"], // A shape
  minor: ["x", "0", "2", "2", "1", "0"], // Am shape
  diminished: ["x", "x", "0", "1", "0", "1"], // Adim shape
  augmented: ["x", "0", "3", "2", "2", "1"], // Aaug shape
  dominant7: ["x", "0", "2", "0", "2", "0"], // A7 shape
  major7: ["x", "0", "2", "1", "2", "0"], // Amaj7 shape
  minor7: ["x", "0", "2", "0", "1", "0"], // Am7 shape
  minorMajor7: ["x", "0", "2", "1", "1", "0"], // AmM7 shape
  sus2: ["x", "0", "2", "2", "0", "0"], // Asus2 shape
  sus4: ["x", "0", "2", "2", "3", "0"], // Asus4 shape
} as const

export function getNotesInScale(root: Note, scale: keyof typeof SCALES): Note[] {
  const rootIndex = NOTES.indexOf(root)
  return SCALES[scale].map((interval) => {
    const noteIndex = (rootIndex + interval) % 12
    return NOTES[noteIndex]
  })
}

export function getNextNote(note: Note, semitones: number): Note {
  const currentIndex = NOTES.indexOf(note)
  const nextIndex = (currentIndex + semitones) % 12
  return NOTES[nextIndex]
}

export function generateFretboardNotes(
  root: Note,
  scale: keyof typeof SCALES,
  chordPosition?: ChordPosition,
): FretboardNote[][] {
  const scaleNotes = getNotesInScale(root, scale)
  const fretboard = STANDARD_TUNING.map((stringNote, stringIndex) => {
    const notes: FretboardNote[] = []
    let currentNote = stringNote as Note

    for (let fret = 0; fret < 18; fret++) {
      const isHighlighted = scaleNotes.includes(currentNote)
      const isSharp = currentNote.includes("#")
      const isChordTone = chordPosition?.frets[stringIndex] === fret.toString()

      notes.push({
        note: currentNote,
        isHighlighted,
        isSharp,
        isChordTone,
      })
      currentNote = getNextNote(currentNote, 1)
    }

    return notes
  })

  return fretboard.reverse() // Reverse the array to get the correct string order
}

export function generateChordPositions(chordName: string): ChordPosition[] {
  const [root, type = ""] = chordName.split(/(?=[a-z])/i)
  let baseShape: string[]

  switch (type) {
    case "m":
      baseShape = CHORD_SHAPES["minor"]
      break
    case "dim":
      baseShape = CHORD_SHAPES["diminished"]
      break
    case "aug":
      baseShape = CHORD_SHAPES["augmented"]
      break
    case "7":
      baseShape = CHORD_SHAPES["dominant7"]
      break
    case "maj7":
      baseShape = CHORD_SHAPES["major7"]
      break
    case "m7":
      baseShape = CHORD_SHAPES["minor7"]
      break
    case "mM7":
      baseShape = CHORD_SHAPES["minorMajor7"]
      break
    case "sus2":
      baseShape = CHORD_SHAPES["sus2"]
      break
    case "sus4":
      baseShape = CHORD_SHAPES["sus4"]
      break
    default:
      baseShape = CHORD_SHAPES["major"]
  }

  // Find the offset from A (since our shapes are based on A chords)
  const rootIndex = NOTES.indexOf(root as Note)
  const aIndex = NOTES.indexOf("A")
  const offset = (rootIndex - aIndex + 12) % 12

  // Generate positions
  const positions: ChordPosition[] = []
  for (let i = 0; i < 5; i++) {
    const position = i + 1
    const frets = baseShape.map((fret) => {
      if (fret === "x") return "x"
      const adjustedFret = (Number.parseInt(fret) + offset + i * 5) % 12
      return adjustedFret.toString()
    })
    positions.push({ position, frets, isValid: true })
  }

  return positions
}

export function generateChordsForKeyAndScale(key: Note, scale: keyof typeof SCALES): string[] {
  const scaleNotes = getNotesInScale(key, scale)
  let chordTypes: string[]

  if (scale === "Harmonic Minor") {
    chordTypes = ["m", "dim", "aug", "mM7", "7", "maj7", "dim7"]
  } else if (scale === "Minor" || scale === "Pentatonic Minor") {
    chordTypes = ["m", "dim", "m7", "7", "sus2", "sus4"]
  } else {
    chordTypes = ["", "m", "dim", "aug", "7", "maj7", "m7", "sus2", "sus4"]
  }

  const chords = scaleNotes.flatMap((note, index) => {
    const chordType = chordTypes[index % chordTypes.length]
    return `${note}${chordType}`
  })

  return chords
}

function getChordNotes(root: Note, chordType: string): Note[] {
  const rootIndex = NOTES.indexOf(root)
  let intervals: number[]

  switch (chordType) {
    case "":
      intervals = [0, 4, 7]
      break
    case "m":
      intervals = [0, 3, 7]
      break
    case "dim":
      intervals = [0, 3, 6]
      break
    case "aug":
      intervals = [0, 4, 8]
      break
    case "7":
      intervals = [0, 4, 7, 10]
      break
    case "maj7":
      intervals = [0, 4, 7, 11]
      break
    case "m7":
      intervals = [0, 3, 7, 10]
      break
    case "mM7":
      intervals = [0, 3, 7, 11]
      break
    case "sus2":
      intervals = [0, 2, 7]
      break
    case "sus4":
      intervals = [0, 5, 7]
      break
    default:
      intervals = [0, 4, 7]
  }

  return intervals.map((interval) => NOTES[(rootIndex + interval) % 12])
}

