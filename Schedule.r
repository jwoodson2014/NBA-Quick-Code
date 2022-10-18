# File name: Schedule.r
# Author: Jason Woodson
# Date: 10/18/2022
# Purpose: Visualize each NBA team's distribution of home games for the 2022-2023 season

# Import necessary packages
library(tidyverse)
library(teamcolors)
library(cowplot)
library(ggdark)


# Import csv file and perform so basic preprocessing
games <- read.csv('Schedule.csv') %>% 
  mutate(Date = as.Date(Date,format = '%d/%m/%Y'),
         Home.Team = as.factor(Home.Team)) %>% 
  select(Date, Home.Team) %>% 
  group_by(Date, Home.Team) %>% 
  summarise(count = n())

# save the color scheme of each NBA team
team_cols <- league_pal('nba', 1)

# plot the data of each home game for every NBA team, color the points accoridng to the team colors
g1 <- games %>% 
  ggplot(aes(x = Date, y = Home.Team, color = Home.Team))+
  geom_point(size = 6,
             shape = 20)+
  scale_y_discrete(limits = rev)+
  scale_x_date(position = 'top')+
  scale_color_manual(values = team_cols)+
  xlab('')+
  ylab('')+
  dark_theme_grey()
  
  
# change a few elements of the plot and save  
g1 + theme(plot.background = element_rect(fill = "grey25"),
        panel.background = element_blank(),
        panel.grid.major = element_line(color = "grey30", size = 1),
        panel.grid.minor = element_line(color = "grey30", size = 1),
        legend.background = element_blank(),
        axis.text = element_text(size = 15),
        legend.key = element_blank(),
        legend.position = 'none')+
  ggsave('Schedule.png', dpi= 300)

