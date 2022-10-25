# File name: Rating.R
# Author: Jason Woodson
# Date: 10/25/2022
# Purpose: Plot each NBA team's offensive and defensive rating

# Import necessary packages
library(tidyverse)
library(nbastatR)
library(ggimage)
library(rsvg)
library(magick)
library(grid)

# import csv file with offensive and defensive rating for each team (scraped using NBA api in Python)
df <- read.csv('League.csv') %>% 
  select(TEAM_ID, TEAM_NAME, OFF_RATING, DEF_RATING) %>% 
  mutate(URL = 'Check')

# grab the nba logo of each team, format appropriately, and save down on your drive in a folder 'Logos'
for (i in 1:nrow(df)){
  
  id <- df$TEAM_ID[i]
  
  url <- paste0('https://cdn.nba.com/logos/nba/',id,'/primary/L/logo.svg')
  
  im <- magick::image_read(url)
  
  x <- image_transparent(im, 'white')
  
  image_write(x, path = paste0('Logos/',id,'.png'), format = 'png')
  
  df$URL[i] <- paste0('Logos/',id,'.png')
  
}

# plot the offensive and defensive rating for each team
df %>% 
  ggplot(aes(x = DEF_RATING, y = OFF_RATING))+
  geom_hline(yintercept = median(df$OFF_RATING))+
  geom_vline(xintercept = median(df$DEF_RATING))+
  annotate('label', x = 101, y = 123, label = 'Good O, Good D',
           size = 2.5)+
  annotate('label', x = 120, y = 98, label = 'Bad O, Bad D',
           size = 2.5)+
  annotate('rect', xmin = min(df$DEF_RATING), xmax = median(df$DEF_RATING),
           ymin = median(df$OFF_RATING), ymax = max(df$OFF_RATING)+2,
           alpha = .1, fill = 'green')+
  annotate('rect', xmin = median(df$DEF_RATING), xmax = max(df$DEF_RATING)+1,
           ymin = min(df$OFF_RATING), ymax = median(df$OFF_RATING),
           alpha = .1, fill = 'red')+
  ggtitle('Net Rating Landscape',
          subtitle = '10/25/2022')+
  xlab('Defensive Rating')+
  ylab('Offensive Rating')+
  geom_image(aes(image = URL),
             size = .08)+
  theme(panel.background = element_rect('floral white'),
        plot.background = element_rect('floral white'),
        panel.border = element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        plot.title = element_text(face = 'bold'),
        plot.subtitle = element_text(face = 'bold'),
        axis.title.y = element_text(face = 'bold'),
        axis.title.x = element_text(face = 'bold'),
        axis.ticks.y = element_blank(),
        axis.ticks.x = element_blank())

#save the plot
ggsave('Rating.png', height = 8, width = 8, dpi = 300)


