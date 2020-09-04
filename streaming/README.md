
# Azure Machine Learning Examples - Predicting Remaining Useful Life of TurboFan

![ds design](/images/datascience.png)

# Real-Time Inferencing


### Create an Event Hubs namespace. Specify a name for the Event Hubs namespace.

```bash

eventhubns=mleventhubns-$RANDOM
az eventhubs namespace create --name $eventhubns --resource-group $resourceGroupName -l $location

```

### Create an event hub. Specify a name for the event hub

```bash
eventhubns=mleventhub-$RANDOM
az eventhubs eventhub create --name mleventhub --resource-group $resourceGroupName --namespace-name $location

```
