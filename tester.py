from plotnine import ggplot, aes, geom_point, facet_wrap, theme, element_text, labs
from plotnine.data import mtcars

(ggplot(mtcars, aes("wt", "mpg"))
 + geom_point()
 + facet_wrap("~gear")
 + theme(
     # Left align the text within the strip
     strip_text_x=element_text(ha="right"), 
     # Optional: Align the strip background to the left edge
     strip_align_x=0 
 )
)
