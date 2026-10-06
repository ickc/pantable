-- {{< copyright-year 2026 >}} renders "2026" this year, "2026–2027" next, etc.
return {
  ["copyright-year"] = function(args)
    local start_year = pandoc.utils.stringify(args[1])
    local current_year = os.date("%Y")
    if start_year == current_year then
      return pandoc.Str(start_year)
    else
      return pandoc.Str(start_year .. "–" .. current_year)
    end
  end,
}
