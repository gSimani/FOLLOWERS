"use client"

import { useState, useMemo, useEffect } from "react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Fretboard } from "@/components/fretboard"
import { ChordDiagram } from "@/components/chord-diagram"
import type { Note } from "@/types"
import {
  SCALES,
  generateFretboardNotes,
  generateChordPositions,
  generateChordsForKeyAndScale,
} from "@/lib/music-theory"

const NOTES: Note[] = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]

export default function GuitarScaleVisualizer() {
  const [selectedKey, setSelectedKey] = useState<Note>("A")
  const [selectedScale, setSelectedScale] = useState<keyof typeof SCALES>("Major")
  const [selectedChord, setSelectedChord] = useState<string>("A")
  const [currentPosition, setCurrentPosition] = useState(0)

  const availableChords = useMemo(
    () => generateChordsForKeyAndScale(selectedKey, selectedScale),
    [selectedKey, selectedScale],
  )

  useEffect(() => {
    if (availableChords.length > 0 && !availableChords.includes(selectedChord)) {
      setSelectedChord(availableChords[0])
    }
  }, [availableChords, selectedChord])

  const chordPositions = useMemo(() => generateChordPositions(selectedChord), [selectedChord])

  const fretboardData = useMemo(
    () => generateFretboardNotes(selectedKey, selectedScale, chordPositions[currentPosition]),
    [selectedKey, selectedScale, chordPositions, currentPosition],
  )

  const handlePreviousPosition = () => {
    setCurrentPosition((prev) => (prev > 0 ? prev - 1 : chordPositions.length - 1))
  }

  const handleNextPosition = () => {
    setCurrentPosition((prev) => (prev < chordPositions.length - 1 ? prev + 1 : 0))
  }

  return (
    <div className="max-w-full mx-auto p-4 space-y-6">
      <h1 className="text-3xl font-bold text-center mb-6">Guitar Scale Visualizer</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Select value={selectedKey} onValueChange={(value) => setSelectedKey(value as Note)}>
          <SelectTrigger>
            <SelectValue placeholder="Select key" />
          </SelectTrigger>
          <SelectContent>
            {NOTES.map((note) => (
              <SelectItem key={note} value={note}>
                {note}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={selectedScale} onValueChange={(value) => setSelectedScale(value as keyof typeof SCALES)}>
          <SelectTrigger>
            <SelectValue placeholder="Select scale" />
          </SelectTrigger>
          <SelectContent>
            {Object.keys(SCALES).map((scale) => (
              <SelectItem key={scale} value={scale}>
                {scale}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={selectedChord} onValueChange={setSelectedChord}>
          <SelectTrigger>
            <SelectValue placeholder="Select chord" />
          </SelectTrigger>
          <SelectContent>
            {availableChords.map((chord) => (
              <SelectItem key={chord} value={chord}>
                {chord}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <Fretboard fretboardData={fretboardData} />

      <div className="mt-6 space-y-4">
        <ChordDiagram
          position={currentPosition + 1}
          frets={chordPositions[currentPosition].frets}
          isValid={chordPositions[currentPosition].isValid}
          stringLabels={["E", "A", "D", "G", "B", "E"]}
        />

        <div className="flex justify-center gap-4">
          <Button onClick={handlePreviousPosition}>Previous Position</Button>
          <Button onClick={handleNextPosition}>Next Position</Button>
        </div>
      </div>
    </div>
  )
}

