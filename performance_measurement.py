import os
import pandas as pd

#header = ['STATUS','TERM','NB RECV HEARTBEAT', 'NB SEND HEARBEAT',
#                  'NB RECV IWANTTOBECANDIDATE', 'NB SEND IWANTTOBECANDIDATE',
#                  'NB SEND VOTE', 'NB RECV VOTE',
#                  'NB RECV IMTHELEADER', 'NB SEND IMTHELEADER',
#                  'TOTAL NB RECV', 'TOTAL NB SEND', 'TOTAL MSG']

def main():
    path = "perfs/"
    dir_list = os.listdir(path)
    tmp = []
    for file in dir_list:
        df = pd.read_csv(path+file,sep=',')
        tmp.append(df)
    data = pd.concat(tmp, axis=0, ignore_index=True)

    #Remove Leader in the dataframe
    indexLeader = data[data['STATUS'] == 'LEADER'].index
    dataLeader = data.iloc[indexLeader,:]
    data.drop(indexLeader, inplace=True)

    #Mean, Min and Max for the Follower
    dataFollower = data.describe().iloc[[1,3,7], :]

    #Write in csv file
    dataLeader.to_csv(path+'LeaderDescribe.csv',index=True)
    dataFollower.to_csv(path+'FollowerDescribe.csv',index=True)

if __name__ == "__main__":
    main()