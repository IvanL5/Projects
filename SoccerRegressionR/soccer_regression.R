install.packages("OpenML")
install.packages("farff")
install.packages('car')
install.packages('pedometrics')
install.packages('ggfortify')

#Data Collection and Cleaning

library('OpenML')
library('farff')
#Soccer Data https://www.openml.org/search?type=data&status=active&id=43604&sort=runs
GetSoccerData <- getOMLDataSet(data.id = 43604L)
SoccerData <- GetSoccerData$data
attach(SoccerData)

# Minutes_Played in numeric
SoccerData$Minutes_Played <- as.numeric(SoccerData$Minutes_Played)


# weight in numeric (pound to kg)
SoccerData$Weight <- as.numeric(gsub("[a-zA-Z ]", "", SoccerData$Weight))
SoccerData$Weight <- round(0.45359237 * SoccerData$Weight , 2)

# height in numeric (foot and inches to cm)
# This follows similar logic that extract 2 numbers from the string using sub, split them using strsplit and then for each of them convert it into numeric and perform the calculation.
SoccerData$Height <- sapply(strsplit(sub("(\\d+)'(\\d+).*", "\\1-\\2", SoccerData$Height), "-"), function(x) 
  as.numeric(x[1]) * 30.48 + as.numeric(x[2]) * 2.54)

#as.factor converts columns to categorical
SoccerData$International_Reputation <- as.factor(SoccerData$International_Reputation)
SoccerData$Weak_Foot <- as.factor(SoccerData$Weak_Foot)
SoccerData$Skill_Moves <- as.factor(SoccerData$Skill_Move)

# Value in numeric
# Build a vector with the corresponding values of M and K using str_detect(), use str_remove() to remove M and K from the initial vector, and then transform Value as numeric and multiply with the created vector.
library(stringr)
Value_unity <- ifelse(str_detect(Value, 'M'), 1e6, ifelse(str_detect(Value, 'K'), 1e3, 1))
SoccerData$Value <- Value_unity * as.numeric(str_remove(Value, 'K|M'))

#Removes rows with missing values or NA.
SoccerData <- SoccerData[complete.cases(SoccerData), ]
#fixing index after deleting rows with NA
rownames(SoccerData) <- 1:nrow(SoccerData)


#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#

#Regression model 1 : Regressing Goals on predictors

#Created initial model to check linear regression assumptions.
#Removed variables that do not related to a players individual attributes.
#performance related attributes and some categorical variables are removed from predictors.
goals.model.initial <- lm(Goals ~ . - Name - Club - Nationality - ID - Unnamed._0 - ShotsOnGoal - Shots - Assists - Minutes_Played - Games_Played - Games_Started - Overall - Potential - International_Reputation - Value - Yellow_Card - Red_Card, data = SoccerData)

#check for Heteroskedasticity
#Some attributes do not appear to be homoscedastic (non-linear relationship between errors and predictors)
library('car')
crPlots(goals.model.initial)

#Check Normal Q-Q plot for normal distribution of errors
#Light left tail and heavy right tail indicates right-skew of errors
library('ggfortify')
autoplot(goals.model.initial)

#Histogram of errors confirms that errors are right-skewed and not normally distributed.
resid <- resid(goals.model.initial)
hist(resid,
     main="Histogram of Residuals in Goals scored model",
     xlab="Error",
     col=" grey",
     freq = FALSE,
)

#Removing Heteroscedasticity by applying log transformation
goals.model.before.stepVIF <- lm(log(Goals) ~ . - Name - Club - Nationality - ID - Unnamed._0 - ShotsOnGoal - Shots - Assists - Minutes_Played - Games_Played - Games_Started - Overall - Potential - International_Reputation - Value - Yellow_Card - Red_Card, data = SoccerData)

#Check for heteroskedasticity after log transformation
#All attributes appear roughly homoscedastic (roughly linear realtionship between errors and predictors)
crPlots(goals.model.before.stepVIF)

#Check Normal Q-Q plot for normal distribution of errors
#Thin tailed distribution of errors, roughly normally distributed.
autoplot(goals.model.before.stepVIF)

#Histogram of residuals to double check distribution of errors
#Confirmed thin tailed distribution (More data closer to the center of distribution).
#Roughly normally distributed.
resid <- resid(goals.model.before.stepVIF)
hist(resid,
     main="Histogram of Residuals in Goals scored model",
     xlab="Error",
     col=" grey",
     freq=FALSE,
     breaks = seq(from = -2, to = 2, by = 0.20)
)

#Check for Multicollinearity with Variance-Inflation factor (VIF). 
#The model has multicollinearity if any predictor has VIF > 5
vif(goals.model.before.stepVIF)

#Remove variables with VIF > 5
library('pedometrics')
goals.model.after.stepVIF <- stepVIF(goals.model.before.stepVIF,threshold = 5, verbose = TRUE)

#No multicollinearity in predictors, all VIF <= 5.
vif(goals.model.after.stepVIF)

#Select best predictors based on Akaike Information Criterion (AIC)
library('MASS')
null.model <- lm(log(Goals) ~ 1, data = SoccerData)
full.model <- goals.model.after.stepVIF
model.step.both.BIC <- step(null.model,
                      scope = list(lower = null.model, upper = full.model),
                      direction = "both" )

#Check for outliers in the data
#No influential outliers found based on 50% quantile of the F distribution
autoplot(model.step.both.BIC, which = 4, ncol = 1)
p <- model.step.both.BIC$rank
n <- NROW(SoccerData) 
cooks.D <-  cooks.distance(model.step.both.BIC)
influential.outliers <- which(cooks.D > qf(0.50, p + 1, n - p - 1))

#Final regression model for predicting goals
#Intercept removed since it was found to be not statistically different from 0.
goals.model <- lm(log(Goals) ~ 0 + Volleys + SlidingTackle + Reactions + Strength + Stamina + Composure + SprintSpeed + Crossing + Weight + Balance, data = SoccerData)
summary(goals.model)

#Check Normal Q-Q plot for normal distribution of errors
#Thin tailed distribution of errors, roughly normally distributed.
autoplot(goals.model)

#Confirmed thin tailed distribution (More data closer to the center of distribution).
#Roughly normally distributed.
resid <- resid(goals.model)
hist(resid,
     main="Histogram of Residuals in Goals scored model",
     xlab="Error",
     col=" grey",
     freq=FALSE,
     breaks = seq(from = -2, to = 2, by = 0.20)
)

#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#

#Regression model 2: Regressing Value on predictors

#Created initial model to check linear regression assumptions.
#Removed variables that do not related to a players individual attributes.
#performance related attributes and some categorical variables are removed from predictors.
value.model.initial <- lm(Value ~ . - Name - Club - Nationality - ID - Unnamed._0 - ShotsOnGoal - Shots - Assists - Minutes_Played - Games_Played - Games_Started - Overall - Potential - International_Reputation - Goals - Yellow_Card - Red_Card, data = SoccerData)

#check for Heteroskedasticity
#Some attributes do not appear to be homoscedastic (non-linear relationship between errors and predictors)
library('car')
crPlots(value.model.initial)

#Check Normal Q-Q plot for normal distribution of errors
#heavy right tail indicates a somewhat right-skew of errors
library('ggfortify')
autoplot(value.model.initial)

#Histogram of errors confirms that errors are right-skewed and not normally distributed.
resid <- resid(value.model.initial)
hist(resid,
     main="Histogram of Residuals in Value model",
     xlab="Error",
     col=" grey",
     freq = FALSE,
)

#Removing Heteroskedasticity using log transformation
value.model.before.stepVIF <- lm(log(Value) ~ . - Name - Club - Nationality - ID - Unnamed._0 - ShotsOnGoal - Shots - Assists - Minutes_Played - Games_Played - Games_Started - Potential - Overall - International_Reputation - Goals - Yellow_Card - Red_Card, data = SoccerData)

#Check for heteroskedasticity after log transformation
#All attributes appear roughly homoscedastic (roughly linear relationship between errors and predictors)
crPlots(value.model.before.stepVIF)

#Check Normal Q-Q plot for normal distribution of errors
#Heavy tailed distribution of errors, roughly normally distributed.
autoplot(value.model.before.stepVIF)

#Histogram of residuals to double check distribution of errors
#Confirmed heavy tailed distribution (More data on the tails of distribution).
#Roughly normally distributed.
resid <- resid(value.model.before.stepVIF)
hist(resid,
     main="Histogram of Residuals in Value model",
     xlab="Error",
     col=" grey",
     freq=FALSE,
     breaks = seq(from = -2, to = 2, by = 0.20)
)

#Check for Multicollinearity with Variance-Inflation factor (VIF). 
#The model has multicollinearity if any predictor has VIF > 5
vif(value.model.before.stepVIF)

#Remove variables with VIF > 5
library('pedometrics')
value.model.after.stepVIF <- stepVIF(value.model.before.stepVIF,threshold = 5, verbose = TRUE)

#No multicollinearity in predictors, all VIF <= 5.
vif(value.model.after.stepVIF)

#Select best predictors based on Akaike Information Criterion (AIC)
library('MASS')
null.model <- lm(log(Value) ~ 1, data = SoccerData)
full.model <- value.model.after.stepVIF
model.step.both.BIC <- step(null.model,
                            scope = list(lower = null.model, upper = full.model),
                            direction = "both")

#Check for outliers in the data
#No influential outliers found based on 50% quantile of the F distribution
autoplot(model.step.both.BIC, which = 4, ncol = 1)
p <- model.step.both.BIC$rank
n <- NROW(SoccerData) 
cooks.D <-  cooks.distance(model.step.both.BIC)
influential.outliers <- which(cooks.D > qf(0.50, p + 1, n - p - 1))

#Final regression model for predicting market value
value.model <- model.step.both.BIC
summary(value.model)

#Check Normal Q-Q plot for normal distribution of errors
#Heavy tailed distribution of errors, roughly normally distributed.
autoplot(value.model)

#Confirmed heavy tailed distribution (More data on tails of the distribution).
#Roughly normally distributed.
resid <- resid(value.model)
hist(resid,
     main="Histogram of Residuals in Value model",
     xlab="Error",
     col=" grey",
     freq=FALSE,
     breaks = seq(from = -2, to = 2, by = 0.20)
)

#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#

#Regression model 3: Regressing Overall on predictors

#Created initial model to check linear regression assumptions.
#Removed variables that do not related to a players individual attributes.
#performance related attributes and some categorical variables are removed from predictors.
overall.model.initial <- lm(Overall ~ . - Name - Club - Nationality - ID - Unnamed._0 - ShotsOnGoal - Shots - Assists - Minutes_Played - Games_Played - Games_Started - Potential - International_Reputation - Goals - Value - Yellow_Card - Red_Card, data = SoccerData)

#check for Heteroscedasticity
#minimal heteroscedasticity (fairly linear relationship between errors and predictors)
library('car')
crPlots(overall.model.initial)

#Check Normal Q-Q plot for normal distribution of errors
#fat tails distribution of errors
#roughly normally distributed
library('ggfortify')
autoplot(overall.model.initial)

#Histogram of errors confirms that errors have fat-tailed distribution and has a roughly normal distribution.
resid <- resid(overall.model.initial)
hist(resid,
     main="Histogram of Residuals in Overall model",
     xlab="Error",
     col=" grey",
     freq = FALSE,
     breaks = seq(from = -10, to = 10, by = 1)
)

#applying log to response variable for consistency and easy comparison with market value model
overall.model.before.stepVIF <- lm(log(Overall) ~ . - Name - Club - Nationality - ID - Unnamed._0 - ShotsOnGoal - Shots - Assists - Minutes_Played - Games_Played - Games_Started - Potential - International_Reputation - Goals - Value - Yellow_Card - Red_Card, data = SoccerData)

#Check for heteroskedasticity after log transformation
#All attributes appear roughly homoscedastic (roughly linear relationship between errors and predictors)
crPlots(overall.model.before.stepVIF)

#Check Normal Q-Q plot for normal distribution of errors
#Heavy tailed distribution of errors, roughly normally distributed.
autoplot(overall.model.before.stepVIF)

#Histogram of residuals to double check distribution of errors
#Confirmed heavy tailed distribution (More data on the tails of distribution).
#Roughly normally distributed.
resid <- resid(overall.model.before.stepVIF)
hist(resid,
     main="Histogram of Residuals in Overall model",
     xlab="Error",
     col=" grey",
     freq = FALSE,
     breaks = seq(from = -0.15, to = 0.15, by = 0.02)
)

#Check for Multicollinearity with Variance-Inflation factor (VIF). 
#The model has multicollinearity if any predictor has VIF > 5
vif(overall.model.before.stepVIF)

#Remove variables with VIF > 5
library('pedometrics')
overall.model.after.stepVIF <- stepVIF(overall.model.before.stepVIF,threshold = 5, verbose = TRUE)

#No multicollinearity in predictors, all VIF <= 5.
vif(overall.model.after.stepVIF)

#Select best predictors based on Akaike Information Criterion (AIC)
library('MASS')
null.model <- lm(log(Overall) ~ 1, data = SoccerData)
full.model <- overall.model.after.stepVIF
model.step.both.BIC <- step(null.model,
                            scope = list(lower = null.model, upper = full.model),
                            direction = "both")

#Check for outliers in the data
#No influential outliers found based on 50% quantile of the F distribution
autoplot(model.step.both.BIC, which = 4, ncol = 1)
p <- model.step.both.BIC$rank
n <- NROW(SoccerData) 
cooks.D <-  cooks.distance(model.step.both.BIC)
influential.outliers <- which(cooks.D > qf(0.50, p + 1, n - p - 1))

#Final regression model for predicting overall rating.
overall.model <- lm(log(Overall) ~ Reactions + BallControl + Composure + Strength + Acceleration + Skill_Moves + Marking + HeadingAccuracy + Age + ShotPower + Volleys + Crossing + FKAccuracy + Jumping, data = SoccerData)
summary(overall.model)

#Check Normal Q-Q plot for normal distribution of errors
#Heavy tailed distribution of errors, roughly normally distributed.
autoplot(overall.model)

#Confirmed heavy tailed distribution (More data on tails of the distribution).
#Roughly normally distributed.
resid <- resid(overall.model)
hist(resid,
     main="Histogram of Residuals in Overall model",
     xlab="Error",
     col=" grey",
     freq=FALSE,
     breaks = seq(from = -0.2, to = 0.2, by = 0.01)
)

