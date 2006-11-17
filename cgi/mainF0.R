## Tests to verify that we are using the right parameterization and
## contrasts with limma for getting the main effects F for "Class".

## f1 allows to see how similar the Fs are to the Fs from a non-moderated
## statistic. As sample size grows larger, the two should become more and
## more similar.

## The correct contrasts are the ...NI.

## I compare also with the old parameterization.


## To make things more "realistic" we add:

##      - an effect of a continuos covariate (Age); the effect size is
##      controlled by agediff


##      - an effect of a categorical covariate (Class2) with effecgt size
##       controlled by cl2diff

##      - a continuos variable that adds nothing (Age2)

##      - allow fitting only Class; Class and Age; Class, Age, Age2;
##       Class, Age, Age2, Class2 (this is controlled by "other", ie.,
##       the number of other variables in the model)


##     Can change the number of genes, and the number of genes with
##     differential expression and then number of samples and classes;
##     numc is samples per class. To get two classes pass the last two as
##     0, and to get 3 classes pass the alst as 0.






## a few checks for obtaining main effects F with limma

f1 <- function(numc = c(5, 30, 30, 10), other = 1,
               agediff = 0.002, meandiff = 0.0051,
               ngenes = 12, ndiff = 10,
               cl2diff = 0.1) {
##    ngenes <- 12
##    meandiff <- 0.0051
##    agediff <- 0.002
##    ndiff <- 10
    n1 <- numc[1]
    n2 <- numc[2]
    n3 <- numc[3]
    n4 <- numc[4]

    
    genes <- matrix(rnorm(ngenes * (n1 + n2 + n3 + n4)),
                    ncol = (n1 + n2 +
                            n3 + n4))
    covar <- data.frame(Class =
                        factor(rep(c("a", "b", "c", "d"), c(n1, n2, n3, n4))),
                        Age = rnorm(n1 + n2 + n3 + n4),
                        Age2 = rnorm(n1 + n2 + n3 + n4),
                        Class2 =
                        sample(rep(c(0, 1, -1, -2), c(n1, n2, n3, n4))) )
    
    addEffect <- function(x) {
        ## the effect is not constant or equally spaced
        m1 <- rnorm(1,-1.5 * meandiff)
        m2 <- rnorm(1, -0.5 * meandiff)
        m3 <- rnorm(1, 0.5 * meandiff)
        m4 <- rnorm(1, 1.5* meandiff)
        agediffef <- agediff * covar$Age
        meandiff <- rep(c(m1, m2, m3, m4), c(n1, n2, n3, n4))
        cl2eff <- cl2diff* covar$Class2
        x +  meandiff + agediffef + cl2eff
    }
    for (i in 1:ndiff)
        genes[i, ] <- addEffect(genes[i, ])

    covar$Class2 <- factor(covar$Class2)
    
    
    options(contrasts = c("contr.treatment", "contr.poly"))
    
    if(other == 0)
        d0 <- model.matrix( ~ Class, data = covar)
    if(other == 1)
        d0 <- model.matrix( ~ Class + Age, data = covar)
    if(other == 2)
        d0 <- model.matrix( ~ Class + Age + Age2, data = covar)
    if(other == 3)
        d0 <- model.matrix( ~ Class + Age + Age2 + Class2, data = covar)

    
###############3  This is the part for obtaining the contrasts ########
    
    Class <- covar$Class
    
    ##  zz: ojo make sure the order of cvars corresponds with colnames
    colnames(d0)[1:nlevels(Class)] <- c("Intercept", levels(Class)[-1])
    
    constructContrasts <-
        paste("makeContrasts(",
              paste(levels(Class)[-1], "- Intercept", collapse = ", "),
              ", levels = d0)", collapse = "")
    
    contrasts.d0 <- eval(parse(text = constructContrasts))
###############3  End  part for obtaining the contrasts ########
    
    lima.mod.0 <- lmFit(genes, d0)
    lima.mod.0.eb <- eBayes(lima.mod.0)
    lima.mod.0.cr <- contrasts.fit(lima.mod.0,
                                   contrasts.d0)
    lima.mod.0.cr.eb <- eBayes(lima.mod.0.cr)
    
    
    
###################################################################
###################################################################
###################################################################
    constructContrastsNI <-
        paste("makeContrasts(",
              paste(levels(Class)[-1], collapse = ", "),
              ", levels = d0)", collapse = "")
    
    contrasts.d0NI <- eval(parse(text = constructContrastsNI))
###############3  End  part for obtaining the contrasts ########

    lima.mod.0.NI.cr <- contrasts.fit(lima.mod.0,
                                      contrasts.d0NI)
    lima.mod.0.NI.cr.eb <- eBayes(lima.mod.0.NI.cr)
    
    
    
    
    #### Class F without moderation
    if(other == 0)
        fs.class.with.int <- apply(genes, 1, function(x) {
            anova(lm(x ~ Class, data = covar))$F[1]})
    if(other == 1)
        fs.class.with.int <- apply(genes, 1, function(x) {
            anova(lm(x ~ Age + Class, data = covar))$F[2]})
    if(other == 2)
        fs.class.with.int <- apply(genes, 1, function(x) {
            anova(lm(x ~ Age + Age2 + Class, data = covar))$F[3]})
    if(other == 3)
        fs.class.with.int <- apply(genes, 1, function(x) {
            anova(lm(x ~ Age + Age2 + Class2 + Class, data = covar))$F[4]})
    
    
    par(mfrow = c(1, 3))
    plot(fs.class.with.int, lima.mod.0.cr.eb$F, main = "Class F, With intercept")
    abline(0, 1, lty = 2, col = "blue")
    
    plot(fs.class.with.int, lima.mod.0.NI.cr.eb$F, main = "Class F, With intercept, NI mod")
    abline(0, 1, lty = 2, col = "blue")
    
    plot(lima.mod.0.cr.eb$F, lima.mod.0.NI.cr.eb$F, main = "The two limmas")
    abline(0, 1, lty = 2, col = "blue")

    ## compare, for the three class case, with the "usual"
    ## limma approach
    if (FALSE & (sum(numc == 0) == 1) & (other == 0)) {
        dl <- model.matrix( ~ Class - 1, data = covar)
        contrasts.dl <- makeContrasts(Classa - Classb, Classa - Classc, Classb - Classc,
                                      levels = dl)
        fit <- lmFit(genes, dl)
        fit <- contrasts.fit(fit, contrasts.dl)
        fit <- eBayes(fit)
        par(mfrow = c(1, 3))
        plot(fs.class.with.int, fit$F, main = "anova")
        abline(0, 1, lty = 2, col = "blue")
        
        plot(lima.mod.0.NI.cr.eb$F, fit$F, main = "Class F, With intercept, NI mod")
        abline(0, 1, lty = 2, col = "blue")
        
        plot(lima.mod.0.cr.eb$F, fit$F, main = "Previous attempt")
        abline(0, 1, lty = 2, col = "blue")
    }
    if (FALSE & (sum(numc == 0) == 2) & (other == 0)) {
        design <- model.matrix(~ Class)
        fit <- lmFit(genes, design)
        fit <- eBayes(fit)
        plot(fit$t[, 2]^2, lima.mod.0.NI.cr.eb$F, main = "New F, t^2")
        abline(0, 1, lty = 2, col = "blue")
    }
}


####  










### The global model F from limma will not necessarily be the same as the
### true model F as it will only be the same if the design is balanced and
### orthogonal. With a factor, and only one factor, I can produce
### orthogonal contrasts. That is NOT possible necessarily in any other case.

##      F: numeric vector of F-statistics for testing all contrasts
##           simultaneously equal to zero



