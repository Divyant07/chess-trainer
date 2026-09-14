import { useState } from 'react'

function RepertoireSidebar({
  repertoires,
  selectedId,
  onSelect,
  onCreate,
  lines,
  onLineClick,
}) {
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newName, setNewName] = useState('')
  const [newColor, setNewColor] = useState('white')

  function handleCreateSubmit(e) {
    e.preventDefault()
    if (!newName.trim()) return
    onCreate(newName.trim(), newColor)
    setNewName('')
    setShowCreateForm(false)
  }

  return (
    <div className="sidebar">
      <div className="sidebar-section">
        <label htmlFor="repertoire-select">Repertoire</label>
        <select
          id="repertoire-select"
          value={selectedId ?? ''}
          onChange={(e) => onSelect(Number(e.target.value))}
        >
          {repertoires.length === 0 && <option value="">No repertoires yet</option>}
          {repertoires.map((r) => (
            <option key={r.id} value={r.id}>
              {r.name} ({r.color})
            </option>
          ))}
        </select>

        {!showCreateForm ? (
          <button className="link-button" onClick={() => setShowCreateForm(true)}>
            + New repertoire
          </button>
        ) : (
          <form className="create-form" onSubmit={handleCreateSubmit}>
            <input
              type="text"
              placeholder="e.g. My White Repertoire"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              autoFocus
            />
            <select value={newColor} onChange={(e) => setNewColor(e.target.value)}>
              <option value="white">White</option>
              <option value="black">Black</option>
            </select>
            <div className="create-form-actions">
              <button type="submit">Create</button>
              <button type="button" onClick={() => setShowCreateForm(false)}>
                Cancel
              </button>
            </div>
          </form>
        )}
      </div>

      <div className="sidebar-section">
        <label>Saved lines {lines.length > 0 && `(${lines.length})`}</label>
        {lines.length === 0 ? (
          <p className="empty-hint">
            No lines saved yet -- play some moves on the board and hit "Save
            line" to add your first one.
          </p>
        ) : (
          <ul className="lines-list">
            {lines.map((line, i) => (
              <li key={i}>
                <button className="line-button" onClick={() => onLineClick(line)}>
                  {line.text}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}

export default RepertoireSidebar