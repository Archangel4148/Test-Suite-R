process_data <- function(x, y, new_x) {
  plastic <- data.frame(y = y, x = x)

  # Linear model
  plastic.lm <- lm(y ~ x, data = plastic)

  # Capture summary output as text
  summary_output <- capture.output(summary(plastic.lm))
  conf_int <- confint(plastic.lm, level = 0.99)

  new_data <- data.frame(x = new_x)

  # Confidence and prediction intervals
  conf_pred <- predict(plastic.lm, new_data, interval="confidence", level=0.98)
  pred_int <- predict(plastic.lm, new_data, se.fit=T, interval="prediction", level=0.98)
  pred_int_weighted <- predict(plastic.lm, new_data, se.fit=T, interval="prediction", weights=10, level=0.98)

  # Capture ANOVA output as text
  anova_output <- capture.output(anova(plastic.lm))

  # Return results as a list
  return(list(
    summary = paste(summary_output, collapse = "\n"),
    conf_int = conf_int,
    conf_pred = conf_pred,
    pred_int = pred_int,
    pred_int_weighted = pred_int_weighted,
    anova = paste(anova_output, collapse = "\n")
  ))
}
