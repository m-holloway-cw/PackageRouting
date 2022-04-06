#Michael Holloway SID: 001215316

import csv
import datetime

# entry point for the entire program to begin running
def start():
    #import distance and location data
    global distances, locations
    distances, locations = importDistanceList();

    #intial load of trucks
    #manually set to balance loads and group matching addresses together
    truck1Load = ['1', '2', '4', '5', '10', '13', '15', '19', '20', '23', '26', '27', '30', '35', '39'];
    truck2Load = ['3', '7', '8', '11', '12', '17', '18', '21', '22', '24', '29', '31', '33', '34', '36', '37', '38', '40']; 
    #create our truck objects - pass in the load information
    truck1 = Truck(truck1Load);
    truck2 = Truck(truck2Load);

    #variable to allow for easy modification of maximum allowed packages
    global numberOfPackages
    numberOfPackages = 40;

    #load hub with packages that can't leave at 8am(constraints/special notes)
    hub =['6', '9', '14', '16', '25', '28', '32'];

    #import our list of packages
    global packages
    packages = importPackageList(hub, numberOfPackages);


    #iterate through truck #1 to successfully deliver every package on board
    while truck1.packageList:
        #every run find the next closest destination
        packNum, dist, packObj =  findClosestNext(truck1);
        #add the distance traveled to this truck
        truck1.travel(dist);
        #deliver primary package found
        deliverPackage(packObj, packNum, truck1);
        #set the delivery time within this particular package object
        packages.search(packNum).setDelivery(truck1.currentTime);

        #find any package with matching location and deliver to save mileage
        for package in truck1.packageList:
            packageObj = packages.search(package);
            if(packageObj.address == packObj.address):
                if packageObj.id in truck1.packageList:
                    deliverPackage(packageObj, packageObj.id, truck1);
                    packages.search(package).setDelivery(truck1.currentTime);

    #iterate through truck #2 to deliver all packages on board
    #truck 2 manually told to return to pickup additional packages at the hub at a particular time
    while truck2.packageList:
        now = datetime.datetime.now();
        #schedule a time to return to the hub to pickup remaining/delayed packages
        returnToHubTime = now.replace(hour=9, minute=6, second=0, microsecond=0);
        truckTime = truck2.currentTime;
        if(truckTime > returnToHubTime and hub):
            #pickup remaining packages a hub and deliver
            hubIndex = destinationIndex = findLocationIndex('HUB');
            distanceBetween = findDistance(truck2.currentLocation, hubIndex);
            truck2.travel(distanceBetween);
            truck2.currentLocation = hubIndex;

            #grab the package list we already have and combine it with the packages from the hub
            tempArray = hub + truck2.packageList;
            truck2.packageList = tempArray;

            #set the package pickupTime for hub elements
            for p in hub:
                packages.search(p).departureTime = truckTime;
            hub.clear(); #remove all elements from the hub so we don't repeat this

        else:
            #every run find the next closest destination
            packNum, dist, packObj =  findClosestNext(truck2);
            #add the distance traveled to this truck
            truck2.travel(dist);
            #deliver primary package found
            deliverPackage(packObj, packNum, truck2);
            #set the delivery time within this particular package object
            packages.search(packNum).setDelivery(truck2.currentTime);

            #find any package with matching location and deliver to save mileage
            for package in truck2.packageList:
                packageObj = packages.search(package);
                if(packageObj.address == packObj.address):
                    id = str(packageObj.id);
                    if id in truck2.packageList:
                        deliverPackage(packageObj, packageObj.id, truck2);
                        packages.search(package).setDelivery(truck2.currentTime);

    #being interface
    print("Select an option:");
    print("1. package information by id");
    print("2. package information by id and at a specific time");
    print("3. all package information at a specific time");
    print("4. mileage information");
    print("5. exit");

    x = input('option: '); #varibale to use as a switch for interface options
    while x != "5":
        if(x=="1"):
            packID = input('package id: ');
            packObject = packages.search(packID);
            print("-----------------------------------");
            print("Package #", packObject.id);
            print("Address:", packObject.address);
            print("City:", packObject.city);
            print("Zip Code:", packObject.zip);
            print("Package Weight:", packObject.weight);
            print("Deadline:", packObject.deadline);
            print("Delivery Time:", packObject.deliveryTime);
            print("-----------------------------------");
        if(x=="2"):
            packID = input('package id: ');
            timeQuery = input('Enter a time in HH:MM AM/PM format(i.e. 10:00 AM/2:30 PM): ');
            try: #if a single digit is provided for the hour catch the error and reformat
                hour = int(timeQuery[:2]);
                min = int(timeQuery[3:5]);
                period = timeQuery[6:].upper();#force to upper case
            except:
                hour = int(timeQuery[:1]);
                min = int(timeQuery[2:4]);
                period = timeQuery[5:].upper();#force to upper case

            if(period == "PM"): #convert to 24 hour time scale
                if(hour != 12):
                    hour = hour + 12;

            now = datetime.datetime.now();
            queryTime =  now.replace(hour=hour, minute=min, second=0, microsecond=0);
            packObject = packages.search(packID);
            timePickedUp = packObject.departureTime;
            timeDelivered = packObject.deliveryTime;
            #set a default status and test values against queryTime
            status = "At the hub";
            if(queryTime > timePickedUp and queryTime < timeDelivered):
                timeOutput = timeDelivered.strftime('%H:%M %p');
                status = "Out for delivery, ETA: " + timeOutput;
            elif(queryTime >= timeDelivered):
                timeOutput = timeDelivered.strftime('%H:%M %p');
                status = "Delivered at: " + timeOutput;

            #print package information to user
            print("-----------------------------------");
            print("Package #", packObject.id);
            print("Address:", packObject.address);
            print("City:", packObject.city);
            print("Zip Code:", packObject.zip);
            print("Package Weight:", packObject.weight);
            print("Deadline:", packObject.deadline);
            print("Stauts:", status);
            print("-----------------------------------");
        if(x=="3"):
            #printout all package information at given time
            timeQuery = input('Enter a time in HH:MM AM/PM format(i.e. 10:00 AM/2:30 PM): ');
            try: #if a single digit is provided for the hour catch the error and reformat
                hour = int(timeQuery[:2]);
                min = int(timeQuery[3:5]);
                period = timeQuery[6:].upper();#force to upper case
            except:
                hour = int(timeQuery[:1]);
                min = int(timeQuery[2:4]);
                period = timeQuery[5:].upper();#force to upper case
            if(period == "PM"): #convert to 24 hour time scale
                if(hour != 12):
                    hour = hour + 12;
            now = datetime.datetime.now();
            queryTime =  now.replace(hour=hour, minute=min, second=0, microsecond=0);
            print("-----------------------------------");

            #iterate through entire package list and print info
            for packID in range(1, numberOfPackages + 1): #known number of packages
                status = "At the hub";
                packObject = packages.search(str(packID));
                timePickedUp = packObject.departureTime;
                timeDelivered = packObject.deliveryTime;
                status = "At the hub";
                if(queryTime > timePickedUp and queryTime < timeDelivered):
                    timeOutput = timeDelivered.strftime('%H:%M %p');
                    status = "Out for delivery, ETA: " + timeOutput;
                elif(queryTime >= timeDelivered):
                    timeOutput = timeDelivered.strftime('%H:%M %p');
                    status = "Delivered at: " + timeOutput;

                #print all package information - condensed to save visual space on screen
                print("Package #:" + packObject.id + " address: " + packObject.address + ", " + packObject.city + ", " + packObject.zip + " weight: " + packObject.weight + " deadline: " + packObject.deadline + " status: " + status );

        if(x=="4"): #printout truck mileages
            truck1Miles = truck1.distanceTraveled;
            truck2Miles = truck2.distanceTraveled;
            print("-----------------------------------");
            print('Truck #1 mileage: ' + str(round(truck1Miles,2)));
            print('Truck #2 mileage: ' + str(round(truck2Miles,2)));
            print('total miles: ',round(truck1Miles + truck2Miles, 2));
            print("-----------------------------------");

        #loop through UI to menu
        print("Select an option:");
        print("1. package information by id");
        print("2. package information by id and at a specific time");
        print("3. all package information at a specific time");
        print("4. mileage information");
        print("5. exit");
        x = input('option: ');

#end main process


#start functions

#function to process our csv file and setup the data for distances/locations
#returns distanceList - a 2d array designed to allow for quick reference
#returns locationList - a list to help convert addresses to indexes
def importDistanceList():
    filename = "distanceData.csv"
    distanceList = []
    locationList = []
    with open(filename,'r') as data:
        for line in csv.reader(data, delimiter=","):
            individualDistanceList = [];
            for d in line:
                if(d.replace('.','',1).isdigit()):
                    individualDistanceList.append(d);
            address = line[1].strip().split('\n')[0];
            locationList.append(address);
            distanceList.append(individualDistanceList);
    return distanceList, locationList;

#function to process csv file for packages
#creates individual package objects that are added the the hash table for lookup speed
#returns the HashTable object packageTable
def importPackageList(hub, size):
    filename = "packageData.csv"
    packageTable = HashTable(size);
    with open(filename,'r') as data:
        for line in csv.reader(data, delimiter=","):

            id = line[0];
            address = line[1];
            pickupTime = datetime.datetime.now().replace(hour=8, minute=0, second=0, microsecond=0);
            for p in hub:
                if id == p:
                    pickupTime = datetime.datetime.now().replace(hour=9, minute=6, second=0, microsecond=0);
            deadline = line[5];
            city = line[2];
            zip = line[4];
            weight = line[6];
            #create package objects and add to packageList
            packObj = package(id, address, pickupTime, deadline, city, zip, weight);

            packageTable.insert(id, packObj);

    return packageTable;



#convert address name to the indexed location
#returns the index of the item so we can crossrefernce with our distance table
def findLocationIndex(addr):
    for items in locations:
        if addr in items:
            index = locations.index(items);
            return index;

#distance from indexed location to indexed location, each machtes index with location in distance array, use addres to find index
#returns the mileage between the 2 specified locations
def findDistance(curr, dest):
    return distances[curr][dest];

#remaining packages in truck, find closest next location
#returns the information for the closest package as well as the package object itself
def findClosestNext(truck):
    lowestDist = 999;
    lowestID = '000';
    for packageID in truck.packageList:
        packageObj = packages.search(packageID);
        packageLocIndex = findLocationIndex(packageObj.address);
        dist = findDistance(truck.currentLocation, packageLocIndex);
        f = float(dist);
        if (f < lowestDist):
            lowestDist = float(dist);
            lowestID = packageID;
    return lowestID, lowestDist, packageObj;

#interacts with the package to set delivery status
#sends a call to deliver the package in this truck object
def deliverPackage(package, packageID, truck):
    package.status = "delivered";
    truck.deliver(packageID);

#easy function to set the status of the package specified
def packageInTransit(package):
    package.status = "out for delivery";


#begin classes

#class to hold and interact with information on each truck
class Truck:
    def __init__(self, packageList):
        self.packageList = packageList;
        self.currentLocation = findLocationIndex('HUB');
        self.distanceTraveled = 0;
        self.speed = 18;
        self.currentTime = datetime.datetime.now().replace(hour=8, minute=0, second=0, microsecond=0); #set starting time

    def deliver(self, pack):
        self.packageList.remove(pack);

    def travel(self, distance):
        self.distanceTraveled = self.distanceTraveled + float(distance);
        timeTraveled = float(distance)/self.speed; #divide number of miles by miles per hour speed
        self.currentTime = self.currentTime + datetime.timedelta(hours = timeTraveled); #add appropriate partial of hour

    def addTimeByDistance(self, miles):
        timeTraveled = miles/self.speed; #divide number of miles by miles per hour speed
        self.currentTime = self.currentTime + datetime.timedelta(hours = timeTraveled); #add appropriate partial of hour

#class to hold and set delivery status for each package object
class package:
    def __init__(self, id, address, departureTime, deadline, city, zip, weight):
        self.id = id;
        self.address = address;
        self.deadline = deadline;
        self.city = city;
        self.zip = zip;
        self.weight = weight;
        self.status = "At the HUB";
        self.departureTime = departureTime;
        self.deliveryTime = datetime.datetime.now().replace(hour=8, minute=0, second=0, microsecond=0);

    def setDelivery(self, time):
        self.deliveryTime = time;

#an empty class to use as a placeholder in HashTable
class EmptyItem:
    pass

#class to hold our hash table
#brings in packages, indexes them based on a hash key
#using linearing probing to handle collisions
#function to insert an object with a given key
#function to retrieve the object based on mimicing the insert functions hash design
#function to remove the object and indexed information give the key
class HashTable:
    def __init__(self, size):
        self.EMPTY_AT_START = EmptyItem();
        self.EMPTY_AFTER_REMOVE = EmptyItem();

        self.table = [self.EMPTY_AT_START] * size;

        #take in the key(our package id) and the obj(package object)
    def insert (self, key, obj):
        #set our hashed index based on key and table size
        bucketKey = hash(key) % len(self.table);
        #utilize a key and package object so we can retrieve easily
        bucketList = [key, obj];

        #linear search of our table based on hashed key location
        bucketIndex = 0;
        while bucketIndex < len(self.table):
            #test expected bucket location
            #if filled with EmptyItem insert the paired key and package object
            if type(self.table[bucketKey]) is EmptyItem:
                self.table[bucketKey] = bucketList;
                return True;
            bucketKey = (bucketKey + 1) % len(self.table);
            bucketIndex = bucketIndex + 1;

        #return false if we can't find a location for this key within the table
        return False;

        #take in the package id as the key
    def search (self, key):
        #set our hashed index based on the key and table size
        bucketKey = hash(key) % len(self.table);

        bucketIndex = 0;

        #search starting at expected location and increase index until found
        while self.table[bucketKey] is not self.EMPTY_AT_START and bucketIndex < len(self.table):
            #get the id value from the expected bucket location
            value = (self.table[bucketKey]);
            if value[0] == key:
                retValue = self.table[bucketKey]
                #return the package object to the reqeust
                return retValue[1];

            # +1 the key if the bucket is already in use and doesn't match our id
            # collabs with our insert function to ensure the exact location is found
            bucketKey = (bucketKey + 1) % len(self.table);
            bucketIndex = bucketIndex + 1;

        #if key isn't found
        return None;

        #take in the package id as the key
    def remove (self, key):
        #set our hashed index based on the key and table size
        bucketKey = hash(key) % len(self.table);

        bucketIndex = 0;

        #search starting at expected location and increase index until found
        #ignore empty locations and fail if not found within the size of the table
        while self.table[bucketKey] is not self.EMPTY_AT_START and bucketIndex < len(self.table):
            #get the id value from the expected bucket location
            value = (self.table[bucketKey]);
            if value[0] == key:
                #if found, set to our EmptyItem class under the removed name
                self.table[bucketKey] = self.EMPTY_AFTER_REMOVE;

            # +1 the key if the bucket is already in use and doesn't match our id
            # collabs with our insert function to ensure the exact location is found
            bucketKey = (bucketKey + 1) % len(self.table);
            bucketIndex = bucketIndex + 1;

        #if key isn't found
        return None;

#begin the program
start();
