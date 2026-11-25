const previews = {
  "ten-day-ultimatum": "คนแปลกหน้าสิบคนตื่นขึ้นรอบโต๊ะในห้องที่ไม่รู้จัก ชายสวมหน้ากากยืนรออยู่ข้างนาฬิกา และไม่มีใครจำได้ว่ามาถึงที่นี่อย่างไร ทุกคนต้องหาคำตอบว่าห้องนี้คืออะไร และทำไมพวกเขาถึงถูกพามาที่นี่",
};

export function bookSynopsis(book) {
  return book.synopsis?.trim() || previews[book.slug] || "";
}
