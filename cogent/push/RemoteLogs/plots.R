library(ggplot2)

mainProfile = read.csv("profile.log")

plt <- ggplot(mainProfile,aes(Total))
plt <-  geom_point()

