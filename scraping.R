# TODO - set this up to cycle through different proxies
# any way to multithread? this might be too slow...

library(XML)
library(RCurl)

setwd("E:/Data/Dropbox/unclaimedProperty")


start <- 1
end <- 200


opts <- list(
  proxy         = "151.200.170.146", 
  proxyusername = "", 
  proxypassword = "", 
  proxyport     = 80,
  ssl.verifypeer = FALSE
)

csvOut <- matrix(nrow = end - start + 1, ncol = 10)

proc.time.start <- proc.time()
for (i in start:end) {
  retrieveID = as.character(i)
  w = getURL(paste0("https://ucpi.sco.ca.gov/ucp/NoticeDetails.aspx?propertyRecID=",retrieveID), 
               .opts = opts)
  html <- htmlParse(w)
  tables <- readHTMLTable(html)
  output <- tables[[2]]
  output <- t(as.matrix(output[6:14, 2]))
  csvOut[i, ] <- cbind(retrieveID, output)
}
(proc.time.tot <- proc.time() - proc.time.start)
  
colnames(csvOut) <- c("retrieveID", "bizCont", "propType", "cash", "shares", "nameSec", "dateRep", "dateCont", "Owner", "OwnerAdd")


# write regex to remove whitespace
csvOut2 <- gsub("\r\n                                                ", "\n", csvOut)
csvOut3 <- gsub("\n\n", "\n", csvOut2)
csvOut4 <- gsub("\n\n", "\n", csvOut3)

write.csv(csvOut4, "output.csv", row.names = F) 