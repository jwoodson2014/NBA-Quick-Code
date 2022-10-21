# File name: NewPlayer.r
# Author: Jason Woodson
# Date: 10/20/2022
# Purpose: Visualize the percentage of minutes in the 1st game that came from players who were not on the team in the prior year

# import necessary packages
library(nbastatR)
library(tidyverse)
library(scales)

# grab the rosters for every team in both 2022 and 2023
rost_22 <- nbastatR::seasons_rosters(seasons = 2022)
rost_23 <- nbastatR::seasons_rosters(seasons = 2023)

# select necessary columns and rename them accordingly
summ_22 <- rost_22 %>% 
  select(idPlayer, idTeam) %>% 
  rename(Player = idPlayer,
         Team_2022 = idTeam)

summ_23 <- rost_23 %>% 
  select(idPlayer, idTeam) %>% 
  rename(Player = idPlayer,
         Team_2023 = idTeam)

# merge the two data frames together on the playerid so you have the 2022 and 2023 team for each player in each year
all_summ <- merge(summ_22, summ_23, by = 'Player', all = T) %>% 
  mutate(Same_team = case_when(Team_2022 == Team_2023 ~ 0, # if the teamid is the same for both 2022 and 2023 = 0, all other cases = 1
                               TRUE ~ 1))

# grab the game logs for the 2023 season (filter for dates or teams you want if you want to drill down)
gl <- game_logs(seasons = 2023)

# add a column in the game logs data to indicate whether a player is on the same team as last year
gl$SameTeam <- 'Check'

# for each player in the game logs data, find whether that player is on the same team as the prior season
for (i in 1:nrow(gl)){
  
  x <- which(gl$idPlayer[i] == all_summ$Player)
  
  gl$SameTeam[i] <- all_summ$Same_team[x]
  
  
}

# summarise the data by each team and calculate the proportion of minutes played by new players
gl_summ <- gl %>% 
  group_by(slugTeam) %>% 
  summarise(Total_Min = sum(minutes),
            New_Min = sum(minutes[SameTeam == 1]),
            Ratio = New_Min / Total_Min)

# plot the data
p1 <- gl_summ %>% 
  select(slugTeam, Ratio) %>% 
  ggplot(aes(Ratio, reorder(slugTeam, desc(Ratio)), fill = Ratio))+
  geom_col()+
  geom_text(aes(x = Ratio, y = reorder(slugTeam, desc(Ratio)),
                label = paste0(round(Ratio*100,0),'%'),
                hjust = -.2),
            size = 3)+
  scale_y_discrete(limits = rev)+
  scale_x_continuous(labels = scales::percent_format(accuracy = 1),
                     limits = c(0,1),
                     expand = c(0,0))+
  scale_fill_gradient(high = 'darkgreen',
                      low = 'lightgreen')+
  ggtitle('Percentage of Minutes by New Players',
          subtitle = '1st Game')+
  ylab('')+
  xlab('')+
  theme(panel.background = element_rect('floral white'),
           plot.background = element_rect('floral white'),
           panel.border = element_blank(),
           panel.grid.minor = element_blank(),
           panel.grid.major = element_blank(),
           legend.position =  'none',
           plot.title = element_text(hjust = .5,
                                     size = 15,
                                     face = 'bold'),
           plot.subtitle = element_text(hjust = .5,
                                        size = 12,
                                        face = 'bold'),
           axis.text.y = element_text(size = 9),
           axis.text.x = element_blank(),
           axis.ticks = element_blank())

# save the plot
ggsave('NewPlayer_Game1.png', dpi = 300)

dev.off()
