# BikeWorks

This repo is the logical representation of the Bike application
that is made up of many microservices.

## MicroServices

* Bike Frontend
  * Provides the base html pages for the web site
* Bike Login
  * Provides the user login and management, including assigning feature set to a user
* Bike Frame
  * Provides the frame image to the frontend
* Bike Seat
  * Provides the seat image to the front end
* Bike Front Wheel
  * Provides the front wheel image to the front end
* Bile Rear Wheel
  * Provides the rear wheel image to the front end

## Feature Sets

Deployment and configuration of the Istio Routing are done through [Feature Set
TOML file](featureset.toml).   Each Feature Set is defined based on the microservice versions it
needs to consume.  The Kubernetes cluster and Istio Routing will be updated by
Deployhub to reflect the feature set definition.  

In addition, the feature set file determines which end users get which features.
