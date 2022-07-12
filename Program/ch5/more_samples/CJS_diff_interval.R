library(marked)
library(readr)

args = commandArgs(trailingOnly=TRUE)
# read file
capturing_history = read_lines(args[1], n_max = -1)
ch <- c(capturing_history)

ip_cluster = read_lines(args[2], n_max = -1)
cluster <- c(ip_cluster)

cluster <- factor(cluster)
DT <- data.frame("ch" = ch, "cluster" = cluster)
DT$ch <- as.character(DT$ch)

start_time <- Sys.time()
# if( args[3] == "1") {
#     DT.proc <- process.data(DT, groups="cluster")
# } else if (args[3] == "2") {
#     DT.proc <- process.data(DT, groups="cluster", time.intervals = c(2,2,2,2,2,2,1,1,2,2))
# } else if (args[3] == "3") {
#     DT.proc <- process.data(DT, groups="cluster", time.intervals = c(3,3,3,3,3,3,1,1,1,3,3))
# } else if (args[3] == "4") {
#     DT.proc <- process.data(DT, groups="cluster", time.intervals = c(4,4,4,4,4,4,1,1,1,1,4,4))
# }
DT.proc <- process.data(DT, groups="cluster")
DT.ddl <- make.design.data(DT.proc)

Phi.cluster.time <- list(formula=~cluster*time)
p.cluster.time <- list(formula=~cluster*time)
# if( args[3] == "1") {
#     cjs.m2 <- crm(DT.proc, DT.ddl, model.parameters = list(Phi = Phi.cluster.time, p = p.cluster.time), accumulate = FALSE)
# } else if (args[3] == "2") {
#     cjs.m2 <- crm(DT.proc, DT.ddl, model.parameters = list(Phi = Phi.cluster.time, p = p.cluster.time), accumulate = FALSE, time.intervals = c(2,2,2,2,2,2,1,1,2,2))
# } else if (args[3] == "3") {
#     cjs.m2 <- crm(DT.proc, DT.ddl, model.parameters = list(Phi = Phi.cluster.time, p = p.cluster.time), accumulate = FALSE, time.intervals = c(3,3,3,3,3,3,1,1,1,3,3))
# } else if (args[3] == "4") {
#     cjs.m2 <- crm(DT.proc, DT.ddl, model.parameters = list(Phi = Phi.cluster.time, p = p.cluster.time), accumulate = FALSE, time.intervals = c(4,4,4,4,4,4,1,1,1,1,4,4))
# }
cjs.m2 <- crm(DT.proc, DT.ddl, model.parameters = list(Phi = Phi.cluster.time, p = p.cluster.time), accumulate = FALSE)
cjs.m2 <- cjs.hessian(cjs.m2)
print(predict(cjs.m2))

end_time <- Sys.time()
print(end_time-start_time)