const titleOverrides = {
  "horror-game-developer": {
    title: "Horror Game Developer: My Games Aren't That Scary!",
    thaiTitle: "นักพัฒนาเกมสยองขวัญ: เกมของผมไม่ได้น่ากลัวขนาดนั้นซะหน่อย!",
  },
};

export function getBookTitlePair(book) {
  const override = titleOverrides[book?.slug] || {};
  const title = override.title || book?.title || "";
  const thaiTitle = override.thaiTitle || book?.thaiTitle || "";

  return {
    title,
    thaiTitle: thaiTitle && thaiTitle !== title ? thaiTitle : "",
  };
}
