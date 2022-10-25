# File name: Rating.R
# Author: Jason Woodson
# Date: 10/25/2022
# Purpose: Plot each NBA team's Accuracy and Frequency is various shooting zones

# import necessary packages
library(tidyverse)
library(ggimage)
library(rsvg)
library(magick)
library(grid)
library(nbastatR)

# increase connection size to scrape team info
Sys.setenv('VROOM_CONNECTION_SIZE' = 131072 *2)

# use nbastatr package to get team IDs
df_ids <- nbastatR::nba_teams(league = 'NBA') %>% 
  filter(isNonNBATeam == 0)

# import data from Cleaning the Glass and merge the frequency and accuracy data
df_freq <- read.csv('league_offense_shooting_frequency_10_25_2022.csv') %>% 
  slice(2:nrow(.)) %>% 
  select(Team, Rim) %>% 
  rename(Rim_Freq = Rim) %>% 
  mutate(Rim_Freq = as.numeric(sub('%','',Rim_Freq)))

df_acc <- read.csv('league_offense_shooting_accuracy_10_25_2022.csv') %>% 
  slice(2:nrow(.)) %>% 
  select(Team, Rim) %>% 
  rename(Rim_Acc = Rim) %>% 
  mutate(Rim_Acc = as.numeric(sub('%','',Rim_Acc)))

df_all <- merge(df_freq, df_acc, by = 'Team') %>% 
  mutate(Logo = 'Fill')

# assign the correct teamid to each team
for (i in 1:nrow(df_all)){
  
  x <- which(df_all$Team[i] == df_ids$cityTeam)
  
  id <- df_ids$idTeam[x]
  
  ifelse(length(x) == 0, 'Fill', df_all$Logo[i] <- paste0('Logos/',id,'.png'))

}

df_all <- df_all %>% 
  mutate(Logo = case_when(Team == 'LA Clippers' ~ 'Logos/1610612746.png',
                          Team == 'LA Lakers' ~ 'Logos/1610612747.png',
                          TRUE ~ Logo))

# plot the data
df_all %>% 
  ggplot(aes(x = Rim_Freq, y = Rim_Acc))+
  geom_hline(yintercept = median(df_all$Rim_Acc))+
  geom_vline(xintercept = median(df_all$Rim_Freq))+
  ggtitle('Accuracy vs. Frequency - Shots at the Rim',
          subtitle = '10/25/2022')+
  labs(caption = 'Data via Cleaning the Glass')+
  xlab('Frequency of Shots at the Rim')+
  ylab('Shooting Percentage on Shots at the Rim')+
  geom_image(aes(image = Logo),
             size = .08)+
  theme(panel.background = element_rect('floral white'),
        plot.background = element_rect('floral white'),
        panel.border = element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        plot.title = element_text(face = 'bold'),
        plot.subtitle = element_text(face = 'bold'),
        plot.caption = element_text(face = 'bold',
                                    size = 5),
        axis.title.y = element_text(face = 'bold'),
        axis.title.x = element_text(face = 'bold'),
        axis.ticks.y = element_blank(),
        axis.ticks.x = element_blank())

# save the plot
ggsave('Frequency Vs. Accuracy - Rim.png',
       height = 6,
       width = 6,
       dpi = 300)