const API_URL = "https://social-media-production-0ef2.up.railway.app";

export async function getPosts() {
  const res = await fetch(`${API_URL}/posts`);
  if (!res.ok) throw new Error("Error al traer posts");
  return res.json();
}