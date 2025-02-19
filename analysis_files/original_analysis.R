plastic<-read.table("http://www.cnachtsheim-text.csom.umn.edu/Kutner/Chapter%20%201%20Data%20Sets/CH01PR22.txt", header=F, col.names=c("y", "x"))
attach(plastic)

summary(plastic)
plastic.lm<-lm(y~x)
summary(plastic.lm)

#confidence interval
confint(plastic.lm, level =0.99)

#confidence interval prediction
new_data <- data.frame(x=30)
predict(plastic.lm, new_data, interval="confidence", level=0.98)

#prediction interval
predict(plastic.lm, new_data, se.fit=T, interval="prediction", level=0.98)

#prediction interval of 10 objects
predict(plastic.lm, new_data, se.fit=T, interval="prediction", weights= 10, level=0.98)

#ANOVA:
anova(plastic.lm)
