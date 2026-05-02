# Simulated example data
set.seed(42)
data <- data.frame(
  newlable = rep(c(
    "This is a very long label for Group A that indicates what it is that is, really.",
    "Group B with detailed description",
    "A third group with another long name",
    "Group D - expanded name",
    "E Group (Special Category)",
    "F - Grouping explanation continues",
    "Seventh Group that has long label"
  ), each = 3),
  vals = rep(c("Category 1", "Category 2", "Category 3"), times = 7),
  anz = sample(20:100, 21, replace = TRUE)
)

data$newlable <- factor(data$newlable, levels = rev(unique(data$newlable)))
data$vals <- factor(data$vals, levels = c("Category 1", "Category 2", "Category 3"))

data <- data |>
  dplyr::group_by(newlable) |>
  dplyr::mutate(
    percent = round(anz / sum(anz) * 100, 1),
    percent_label = paste0(percent, "%")
  ) |>
  dplyr::ungroup()

labels <- list(
  labels = levels(data$vals),
  colors = c("#4E79A7", "#F28E2B", "#E15759")
)



ggplot2::ggplot(data, ggplot2::aes(x = "", y = percent, fill = vals)) +
  ggplot2::geom_bar(stat = "identity", position = "stack", width = 1) +  # Slightly thicker bars
  ggplot2::geom_text(
    ggplot2::aes(label = percent_label, group = vals),
    position = ggplot2::position_stack(vjust = 0.5),
    size = 3,
    color = "white",
    fontface = "bold"
  )+
  ggplot2::facet_wrap(~ newlable, ncol = 1, strip.position = "top") +
  ggplot2::scale_fill_manual(
    breaks = rev(labels$labels),
    values = rev(labels$colors),
    drop = TRUE,
    labels = function(x) stringr::str_wrap(x, width = 15)
  )+
  ggplot2::scale_x_discrete(
    guide = ggplot2::guide_axis(n.dodge = 1),
    labels = rev(levels(labels$labels)),
    limits = rev(levels(labels$labels))
  ) +
  ggplot2::scale_y_continuous(
    breaks = function(x) scales::pretty_breaks()(x) |> round(),
    labels = scales::number_format(accuracy = 1)
  )+
  ggplot2::coord_flip() +
  ggplot2::theme_minimal(base_size = 14) +
  ggplot2::theme(
    legend.position = "bottom",
    legend.box.margin = ggplot2::margin(10, 10, 10, 10),
    legend.spacing.y = ggplot2::unit(0.5, "cm"),
    legend.spacing.x = ggplot2::unit(0.5, "cm"),
    legend.key.size = ggplot2::unit(0.75, "lines"),
    legend.text = ggplot2::element_text(size = 11, color = "gray30"),
    axis.text = ggplot2::element_text(size = 12),
    axis.title = ggplot2::element_text(size = 12),
    axis.text.x = ggplot2::element_text(size = 8, color = "gray70"),
    axis.ticks.x = ggplot2::element_line(color = "gray70", linewidth = 0.3),
    strip.text = ggtext::element_markdown(
      margin = ggplot2::margin(4, 4, 4, 4),
      size = 11,
      face = "bold",
      hjust = 0
    ),
    panel.spacing.y = ggplot2::unit(0.75, "lines"),
    panel.border = ggplot2::element_blank(),
    panel.grid.major.y = ggplot2::element_line(color = "gray90", linewidth = 0.3),
    plot.margin = ggplot2::margin(10, 15, 10, 15)
  ) +
  ggplot2::labs(
    x = NULL,
    y = "Prozent",
    fill = NULL
  )
