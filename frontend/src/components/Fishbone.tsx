import { useState } from "react"
import { FISH_CATEGORIES } from "../format"
import { useAppDispatch } from "../store/hooks"
import { addBlank, removeItem, updateItem } from "../store/investigationSlice"
import type { FishItem } from "../types"

const TOP = [
  { category: "Man", x: 190, desc: "Personnel, operator qualification, gowning, training, shift handover" },
  { category: "Machine", x: 400, desc: "Process reactors, valves, chilled utilities, instruments, calibration" },
  { category: "Method", x: 610, desc: "Batch records, crystallization recipes, SOPs, cycle durations" },
] as const

const BOTTOM = [
  { category: "Material", x: 190, desc: "Starting raw materials, reagents, solvents, intermediates, catalysts" },
  { category: "Measurement", x: 400, desc: "HPLC assay, LOD moisture, RTDs, pH probes, laboratory methods" },
  { category: "Environment", x: 610, desc: "HVAC cleanroom pressures, humidity, particulates, utilities" },
] as const

const COLOR: Record<string, string> = {
  Man: "#b91c1c",
  Machine: "#0369a1",
  Method: "#15803d",
  Material: "#b45309",
  Measurement: "#6d28d9",
  Environment: "#0f766e",
}

export function Fishbone({ items, problem }: { items: FishItem[]; problem: string }) {
  const dispatch = useAppDispatch()
  const [selectedCategory, setSelectedCategory] = useState<string>("Machine")

  const selectedItems = items.filter((item) => item.category === selectedCategory)

  const handleAddCause = () => {
    dispatch(addBlank({ collection: "fishbone" }))
  }

  return (
    <div className="interactive-fishbone-root">
      <div className="fishbone-instructions">
        <span>Click on any 6M manufacturing bone or category pill below to inspect, edit, or add contributing factors:</span>
      </div>

      <div className="fish-chart">
        <svg viewBox="0 0 980 520" role="img" aria-label="Interactive Ishikawa diagram of the six API manufacturing categories">
          {/* Main Spine */}
          <line x1="70" y1="260" x2="800" y2="260" stroke="#0f172a" strokeWidth="4" />
          <polygon points="800,232 865,260 800,288" fill="#0f766e" />

          {/* Top Ribs */}
          {TOP.map((bone) => (
            <Bone
              key={bone.category}
              category={bone.category}
              x={bone.x}
              upward
              items={items}
              isSelected={selectedCategory === bone.category}
              onSelect={() => setSelectedCategory(bone.category)}
            />
          ))}

          {/* Bottom Ribs */}
          {BOTTOM.map((bone) => (
            <Bone
              key={bone.category}
              category={bone.category}
              x={bone.x}
              upward={false}
              items={items}
              isSelected={selectedCategory === bone.category}
              onSelect={() => setSelectedCategory(bone.category)}
            />
          ))}

          {/* Problem Statement Head */}
          <rect x="872" y="184" width="104" height="152" rx="6" fill="#0f766e" />
          <text x="924" y="206" textAnchor="middle" fill="#ffffff" fontSize="11" fontWeight="bold">
            OBSERVED EVENT
          </text>
          <line x1="880" y1="214" x2="968" y2="214" stroke="#5eead4" strokeWidth="1" />
          {wrap(problem || "Deviation Event", 14)
            .slice(0, 6)
            .map((line, index) => (
              <text
                key={line + index}
                x="924"
                y={232 + index * 16}
                textAnchor="middle"
                fill="#f8fafc"
                fontSize="10"
              >
                {line}
              </text>
            ))}
        </svg>

        {/* Interactive Category Selector Pills */}
        <ul className="fish-legend">
          {FISH_CATEGORIES.map((category) => {
            const count = items.filter((i) => i.category === category).length
            const isSelected = selectedCategory === category
            return (
              <li
                key={category}
                className={`legend-pill ${isSelected ? "selected" : ""}`}
                onClick={() => setSelectedCategory(category)}
              >
                <span className="dot" style={{ background: COLOR[category] }} />
                <strong>{category}</strong>
                <span className="count-chip">({count})</span>
              </li>
            )
          })}
        </ul>
      </div>

      {/* Category Rib Inspector & Editor */}
      <div className="fishbone-category-inspector">
        <div className="inspector-head">
          <div className="inspector-title">
            <span className="cat-swatch" style={{ background: COLOR[selectedCategory] || "#0f766e" }} />
            <div>
              <h4>{selectedCategory} Category Inspection</h4>
              <p className="text-xs text-muted">
                {TOP.find((b) => b.category === selectedCategory)?.desc ||
                  BOTTOM.find((b) => b.category === selectedCategory)?.desc ||
                  "Manufacturing branch factors."}
              </p>
            </div>
          </div>
          <button type="button" className="btn-secondary btn-sm" onClick={handleAddCause}>
            + Add Cause to {selectedCategory}
          </button>
        </div>

        {selectedItems.length === 0 ? (
          <div className="empty-category-notice">
            <p>No contributing factors identified on the {selectedCategory} branch for this event.</p>
            <button type="button" className="text-btn text-teal" onClick={handleAddCause}>
              Click here to add an evaluated factor.
            </button>
          </div>
        ) : (
          <div className="category-items-list">
            {selectedItems.map((item) => (
              <div key={item.id} className="category-item-card">
                <div className="item-input-row">
                  <div className="grow">
                    <label className="text-xs font-semibold text-slate-700">Evaluated Contributing Factor:</label>
                    <input
                      type="text"
                      className="factor-input"
                      value={item.cause}
                      placeholder="e.g. Valve hunting, incorrect solvent staged, operator handover lapse..."
                      onChange={(e) =>
                        dispatch(updateItem({ collection: "fishbone", id: item.id, patch: { cause: e.target.value } }))
                      }
                    />
                  </div>
                  <div className="grow">
                    <label className="text-xs font-semibold text-slate-700">Supporting Evidence / Quote:</label>
                    <input
                      type="text"
                      className="factor-input font-mono text-xs"
                      value={item.evidence}
                      placeholder="Quote from source document verifying this factor..."
                      onChange={(e) =>
                        dispatch(updateItem({ collection: "fishbone", id: item.id, patch: { evidence: e.target.value } }))
                      }
                    />
                  </div>
                </div>

                <div className="item-meta-row">
                  <label className="plausibility-toggle">
                    <input
                      type="checkbox"
                      checked={item.plausible}
                      onChange={(e) =>
                        dispatch(updateItem({ collection: "fishbone", id: item.id, patch: { plausible: e.target.checked } }))
                      }
                    />
                    <span>{item.plausible ? "Active Contributor (Plausible)" : "Ruled Out / Ruled Non-Causal"}</span>
                  </label>

                  <button
                    type="button"
                    className="text-btn danger text-xs"
                    onClick={() => dispatch(removeItem({ collection: "fishbone", id: item.id }))}
                  >
                    Remove Factor
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function Bone({
  category,
  x,
  upward,
  items,
  isSelected,
  onSelect,
}: {
  category: string
  x: number
  upward: boolean
  items: FishItem[]
  isSelected: boolean
  onSelect: () => void
}) {
  const y2 = upward ? 76 : 444
  const causes = items.filter((item) => item.category === category).slice(0, 3)
  const color = COLOR[category] ?? "#0f172a"
  return (
    <g onClick={onSelect} className={`bone-group ${isSelected ? "selected" : ""}`} style={{ cursor: "pointer" }}>
      {/* Rib Line */}
      <line
        x1={x}
        y1="260"
        x2={x - 80}
        y2={y2}
        stroke={color}
        strokeWidth={isSelected ? 3.5 : 2}
        strokeDasharray={isSelected ? "none" : "none"}
      />

      {/* Category Label */}
      <text
        x={x - 86}
        y={upward ? 64 : 464}
        textAnchor="end"
        fill={color}
        fontSize="13"
        fontWeight={isSelected ? "bold" : "600"}
      >
        {category} {isSelected ? "●" : ""}
      </text>

      {/* Branch Causes */}
      {causes.map((cause, index) => (
        <g key={cause.id}>
          <line
            x1={x - 70}
            y1={(upward ? 94 : 402) + (upward ? 1 : -1) * index * 18}
            x2={x - 20}
            y2={(upward ? 94 : 402) + (upward ? 1 : -1) * index * 18}
            stroke={cause.plausible ? color : "#94a3b8"}
            strokeWidth="1"
          />
          <text
            x={x - 65}
            y={(upward ? 91 : 399) + (upward ? 1 : -1) * index * 18}
            fill={cause.plausible ? "#0f172a" : "#64748b"}
            fontSize="10"
            fontWeight={cause.plausible ? "500" : "normal"}
            opacity={cause.plausible ? 1 : 0.65}
          >
            {clip(cause.cause, 34)}
          </text>
        </g>
      ))}

      {causes.length === 0 && (
        <text
          x={x - 70}
          y={upward ? 104 : 408}
          fill="#94a3b8"
          fontSize="10"
          fontStyle="italic"
        >
          (No active factor)
        </text>
      )}
    </g>
  )
}

function clip(value: string, length: number): string {
  const text = value.trim() || "—"
  return text.length > length ? `${text.slice(0, length - 1)}…` : text
}

function wrap(value: string, width: number): string[] {
  const words = value.trim().split(/\s+/).filter(Boolean)
  if (words.length === 0) return ["Observed Event"]
  const lines: string[] = []
  let current = ""
  for (const word of words) {
    const next = current ? `${current} ${word}` : word
    if (next.length > width && current) {
      lines.push(current)
      current = word
    } else {
      current = next
    }
  }
  if (current) lines.push(current)
  return lines
}
