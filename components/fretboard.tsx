"use client"

import type { FretboardNote } from "@/types"

const STANDARD_TUNING = ["E", "B", "G", "D", "A", "E"]

interface FretboardProps {
  fretboardData: FretboardNote[][]
}

export function Fretboard({ fretboardData }: FretboardProps) {
  const fretMarkers = [2, 4, 6, 8, 11, 14, 16]

  return (
    <div className="w-full overflow-x-auto">
      <div className="min-w-full">
        {/* Fret numbers */}
        <div className="flex mb-2">
          <div className="w-8"></div>
          {Array.from({ length: 17 }).map((_, i) => (
            <div key={i} className="flex-1 flex justify-center">
              <span className="text-xs text-gray-500">{i + 1}</span>
            </div>
          ))}
        </div>

        {/* Fret markers */}
        <div className="flex mb-2">
          <div className="w-8"></div>
          {Array.from({ length: 17 }).map((_, i) => (
            <div key={i} className="flex-1 flex justify-center">
              {fretMarkers.includes(i + 1) && (
                <div className={`w-2 h-2 rounded-full bg-gray-300 ${i + 1 === 12 ? "relative" : ""}`}>
                  {i + 1 === 12 && <div className="absolute -top-3 w-2 h-2 rounded-full bg-gray-300" />}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Strings */}
        {fretboardData.map((string, stringIndex) => (
          <div key={stringIndex} className="flex h-10 items-center border-b border-gray-300 last:border-b-0">
            {/* String label */}
            <div className="w-8 text-center font-medium text-sm">{STANDARD_TUNING[stringIndex]}</div>

            {/* Frets */}
            {string.slice(1, 18).map((fret, fretIndex) => (
              <div
                key={fretIndex}
                className="flex-1 border-l border-gray-300 first:border-l-2 first:border-l-gray-400 h-full flex items-center justify-center relative"
              >
                {(fret.isHighlighted || fret.isChordTone) && (
                  <div
                    className={`w-6 h-6 rounded-full flex items-center justify-center text-xs
                      ${
                        fret.isChordTone
                          ? "bg-red-500 text-white"
                          : fret.isHighlighted
                            ? "bg-blue-100 text-blue-600"
                            : ""
                      }`}
                  >
                    {fret.note}
                  </div>
                )}
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}

