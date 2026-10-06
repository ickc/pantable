-- Run the pantable filter, as installed, from Quarto.
--
-- Quarto looks for a JSON filter beside the document rather than on PATH,
-- so the pages list this Lua filter, which hands the document to the
-- pantable executable. pandoc runs it from the page's directory, so an
-- `include` in a table is relative to the page.
function Pandoc(doc)
  return pandoc.utils.run_json_filter(doc, "pantable", { FORMAT })
end
