-- For the pages under examples/: append, in tabs, the Markdown the page is
-- made from, the same with each table as pandoc writes it, and the tables
-- written back as pantable2csvx's code blocks, so that each example shows
-- its input and its result together. HTML only.

local function read(path)
  local f = io.open(path, "r")
  if not f then return nil end
  local text = f:read("a")
  f:close()
  return (text:gsub("%s+$", ""))
end

-- The Markdown pandoc writes for the input, read with these filters.
local function markdown_of(input, filters)
  local args = {}
  for _, f in ipairs(filters) do
    table.insert(args, "--filter")
    table.insert(args, f)
  end
  for _, a in ipairs({ "-t", "markdown", input }) do
    table.insert(args, a)
  end
  local ok, out = pcall(pandoc.pipe, "pandoc", args, "")
  if not ok then
    io.stderr:write("example-source.lua: could not run pandoc for " ..
      input .. "; leaving out its output\n")
    return nil
  end
  return (out:gsub("%s+$", ""))
end

local function tab(tabs, name, text)
  if not text then return end
  tabs:insert(pandoc.Header(3, name, pandoc.Attr("", { "unnumbered" })))
  tabs:insert(pandoc.CodeBlock(text, pandoc.Attr("", { "markdown" })))
end

function Pandoc(doc)
  if not quarto.doc.is_format("html") then return nil end
  local input = quarto.doc.input_file
  -- The examples are .md; the overview page is not one.
  if not input:match("%.md$") then return nil end

  local tabs = pandoc.Blocks({})
  tab(tabs, "Markdown", read(input))
  tab(tabs, "With pantable", markdown_of(input, { "pantable" }))
  tab(tabs, "Back with pantable2csvx", markdown_of(input, { "pantable", "pantable2csvx" }))

  doc.blocks:insert(pandoc.Header(2, "Source", pandoc.Attr("source", { "unnumbered" })))
  doc.blocks:insert(pandoc.Para({ pandoc.Str(
    "This page is made from the Markdown below. The second tab is what " ..
    "pandoc -F pantable -t markdown writes for it, each table as a " ..
    "pandoc table; the third converts those tables back to code blocks " ..
    "with pantable2csvx.") }))
  doc.blocks:insert(pandoc.Div(tabs, pandoc.Attr("", { "panel-tabset" })))
  return doc
end
