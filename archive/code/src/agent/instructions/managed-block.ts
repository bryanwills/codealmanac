export function upsertManagedBlock(
  contents: string,
  start: string,
  end: string,
  block: string,
): string {
  const startIndex = contents.indexOf(start);
  const endIndex = contents.indexOf(end);
  if (startIndex !== -1 && endIndex !== -1 && endIndex > startIndex) {
    const afterEnd = endIndex + end.length;
    return `${contents.slice(0, startIndex)}${block}${contents.slice(afterEnd)}`;
  }

  const sep =
    contents.length === 0 ? "" : contents.endsWith("\n") ? "\n" : "\n\n";
  return `${contents}${sep}${block}\n`;
}

export function removeManagedBlock(
  contents: string,
  start: string,
  end: string,
): { changed: boolean; body: string } {
  const startIndex = contents.indexOf(start);
  const endIndex = contents.indexOf(end);
  if (startIndex === -1 || endIndex === -1 || endIndex < startIndex) {
    return { changed: false, body: contents };
  }

  const afterEnd = endIndex + end.length;
  let body = `${contents.slice(0, startIndex)}${contents.slice(afterEnd)}`;
  body = body.replace(/\n\n\n+/g, "\n\n");
  body = body.replace(/^\n+/, "");
  return { changed: true, body };
}
