export interface Room {
  room_id: number
  status: string // "reacted" | "not_reacted"
  title: string
  link: string
  price: number
  city: string
  size: number
  publication_date: string
  closing_date: string
  allocation_type: string | null
  private_kitchen: boolean
  private_bathroom: boolean
  furnished: boolean
  wifi: boolean
  can_react: boolean
}

export async function getRooms(): Promise<Room[]> {
  const response = await fetch('/api/rooms')
  if (!response.ok) {
    throw new Error(`Failed to load rooms: ${response.status}`)
  }
  return response.json()
}
