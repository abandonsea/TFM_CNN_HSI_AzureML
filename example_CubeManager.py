######################################################################################################
# DESCRIPTION OF THIS SCRIPT:
# Basic script to learn how to use the 'CubeManager' class from 'hsi_dataManager.py' file.
#-----------------------------------------------------------------------------------------------------
# It demonstrates:
#   1) How to create a CubeManager instance
#   2) How to load '_dataset.mat' files to the CubeManager instance for training
#   3) How to create 2D batches with loaded data in the CubeManager instance
#   4) How to convert 2D batches to batch PyTorch tensors with the CubeManager instance
#   5) How to create a FourLayerNet model and how to train it with the batch 
#   6) How to load a single '_dataset.mat' with a new CubeManager instance for testing
#   7) How to predict the test dataset with our trained model
#   8) How to compute prediction metrics and print them
#######################################################################################################

import torch                        # Import PyTorch

import hsi_dataManager as hsi_dm    # Import 'hsi_dataManager.py' file as 'hsi_dm' to load use all desired functions 
import nn_models as models          # Import 'nn_models.py' file as 'models' to define any new Neural Network included in the file 
import metrics as mts               # Import 'metrics.py' file as 'mts' to evluate metrics
import numpy as np                  # Import Numpy as np

#*#############################
#*#### START MAIN PROGRAM #####
#*

# Desired patient images ID
# ['ID0018C09', 'ID0025C02', 'ID0029C02', 'ID0030C02', 'ID0033C02', 'ID0034C02', 'ID0035C02', 'ID0038C02', 'ID0047C02', 'ID0047C08', 'ID0050C05', 'ID0051C05', 'ID0056C02', 'ID0064C04',
# 'ID0064C06', 'ID0065C01', 'ID0065C09', 'ID0067C01', 'ID0068C08', 'ID0070C02', 'ID0070C05', 'ID0070C08', 'ID0071C02', 'ID0071C011', 'ID0071C014']
patients_list_train = ['ID0018C09', 'ID0025C02']
patient_test = ['ID0038C02']

# Directories with data
dir_datasets = "NEMESIS_images/datasets/"
dir_gtMaps = "NEMESIS_images/GroundTruthMaps/"
dir_preProImages = "NEMESIS_images/preProcessedImages/"
dir_rawImages = "NEMESIS_images/tif/"

# Python dictionary to convert labels to label4Classes
dic_label = {'101': 1, '200': 2, '220': 2, '221': 2, '301': 3, '302': 4, '320': 5, '331': 6}

# Determine dimension of batches for the Neural Network
batch_dim = '3D'

# Number of epochs
epochs = 10

# Batch size
batch_size = 16

# K_folds
k_folds = 5

#*####################
#* LOAD TRAIN IMAGES
print("\n##########")
print("Loading training images. Please wait...")

# Create an instance of 'CubeManager'
cm_train = hsi_dm.CubeManager(patch_size = 7, batch_size = batch_size, dic_label = dic_label, batch_dim = batch_dim)

# Load all desired pixels to the 'CubeManager' instance 'cm_train' (all data is stored inside the instance attributes)
cm_train.load_patient_cubes(patients_list_train, dir_gtMaps, dir_preProImages)

print("\tTraining images have been loaded. Creating training batches...")

# Create batches with the loaded data. Returns 'batches' which is a Python dictionary including 2 Python lists, 'data' and 'labels', containing all batches
batches_train = cm_train.create_batches()

"""
# PRINT IN TERMINAL THE SHAPE OF EVERY CREATED BATCH
if ( batch_dim == '2D' ):
    i = 0
    for b in batches_train['data']:
        print('Size of batch ', i+1, ' = ', batches_train['data'][i].shape )
        i += 1

    print('Last batch ', batches_train['data'][i-1] )

elif ( batch_dim == '3D' ):
    i = 0
    for b in batches_train['cube']:
        print('Size of batch ', i+1, ' = ', batches_train['cube'][i].shape )
        i += 1

    print('Last batch ', batches_train['cube'][i-1] )

stop
"""

"""
print("\n\t#####")
print('\t batches_train:')
print("\t\t type(batches_train['cube']) = ", type(batches_train['cube']))
print("\t\t len(batches_train['cube'] = ", len(batches_train['cube']))
print("\t\t type(batches_train['cube'][0]) = ", type(batches_train['cube'][0]))
print("\t\t batches_train['cube'][0].shape = ", batches_train['cube'][0].shape )
print("\t\t batches_train['cube'][0][0].shape = ", batches_train['cube'][0][0].shape )
"""


print("\tTraining batches have been created.")

if ( batch_dim == '2D' ):
    print("\tConverting data and label batches to tensors...")
    # Convert 'data' and 'label4Classes' batches to PyTorch tensors for training our Neural Network
    data_tensor_batch = cm_train.batch_to_tensor(batches_train['data'], data_type = torch.float)
    labels_tensor_batch = cm_train.batch_to_tensor(batches_train['label4Classes'], data_type = torch.LongTensor)

    print("\tTensors have been created.")

"""    
    print('### DEBUG ###')
    print('data_tensor_batch: ')
    print('\t type(data_tensor_batch) = ', type(data_tensor_batch))
    print('\t data_tensor_batch[0].shape = ', data_tensor_batch[0].shape)
    print('\t type(labels_tensor_batch) = ', type(labels_tensor_batch))
    print('\t labels_tensor_batch[0].shape = ', labels_tensor_batch[0].shape)
 """   

#*######################
#* TRAIN NEURAL NETWORK
print("\n##########")
print("Training your Neural Network. Please wait...")

if ( batch_dim == '2D' ):
    # Create a FourLayerNet model, which contains 4 fully connected layers with relu activation functions
    model = models.FourLayerNet(D_in = cm_train.data.shape[-1], H = 16, D_out = cm_train.numUniqueLabels)

    # Train FourLayerNet model
    model.trainNet(batch_x = data_tensor_batch, batch_y = labels_tensor_batch, epochs = epochs, plot = True, lr = 0.01)

elif ( batch_dim == '3D' ):

    print("\tSplitting data before performing K-fold double-cross validation...")
    test_data_folds, test_label_folds, calibration_data_folds, calibration_label_folds, validation_data_folds, validation_label_folds  = hsi_dm.kfold_double_cv_split(batch_data=batches_train['cube'], batch_labels=batches_train['label'], k_folds=k_folds)

    print("\tData has been splitted. Performing ", k_folds ,"fold double-cross validation...")

    # todo: STRUCTURE TO PERFORM DOUBLE_CROSS_VALIDATION()
    print('\n\t### DOUBLE-CROSS VALIDATION ###')
    
    #*###############################################################
    #* FOR ITERATION FOR THE OUTER DOUBLE-CROSS VALIDATION LOOP (K)
    #*
    best_K_OACC = 0
    Kn = 0

    for K in range(0, k_folds, 1):
        print('\n\t\t Current K fold =', K+1)

        #*################################################################
        #* FOR ITERATION FOR THE INNER DOUBLE-CROSS VALIDATION LOOP (Kn)
        #*
        best_Kn_OACC = 0
        
        for _ in range(0, k_folds, 1):
            print('\t\t\t Current Kn fold =', Kn+1)
            
            # Create a Conv2DNet model. We need to define a new one for every Kn iteration
            model = models.Conv2DNet(num_classes = cm_train.numUniqueLabels, in_channels = cm_train.numBands)

            # Convert calibration data to tensor
            batch_x = torch.from_numpy(calibration_data_folds[Kn]).type(torch.float)
            batch_y = torch.from_numpy(calibration_label_folds[Kn]).type(torch.LongTensor)

            # Train CNN in current Kn fold using the calibration data
            model.trainNet(batch_x = batch_x, batch_y = batch_y, epochs = epochs, plot = False, lr = 0.01)

            # Convert validation data to tensor
            batch_x_val = torch.from_numpy(validation_data_folds[Kn]).type(torch.float)

            # Test CNN in current Kn fold using the validation data
            y_hat_Kn = model.predict(batch_x = batch_x_val)

            # Manipulate 'validation_label_folds' for the current 'Kn'.
            # We first need to concatenate all batches together with 'np.concatenate()' along the rows (axis=0)
            # Then we extract the labels and not the coordenates (remember that '_labels_folds' variables have (x_coord, y_coord, label)).
            # Since the result is of shape (N,) and the shape of 'y_hat_Kn' is (N, 1), we need to reshape (-1 indicates to take the entire lenght)
            # We convert it as integers since they originally are floats and we need the labels as indexes inside 'get_metrics()'
            y_true_Kn = np.concatenate(validation_label_folds[Kn], axis = 0)[:, -1].reshape((-1,1)).astype(int)

            # Evaluate metrics by comparing the predicted labels with the true labels for the current Kn fold
            Kn_OACC = mts.get_metrics(y_true_Kn, y_hat_Kn, cm_train.numUniqueLabels)['OACC']

            if (best_Kn_OACC < Kn_OACC):
                print('\t\t\t Found new best model!')
                best_Kn_OACC = Kn_OACC

                # Save Kn CNN model in local variable
                best_Kn_model = model
            
            Kn += 1
        #*
        #* END OF INNER DOUBLE-CROSS VALIDATION LOOP (Kn)
        #*################################################

        # Convert test data to tensor
        batch_x_test = torch.from_numpy(test_data_folds[K]).type(torch.float)

        # Test 'best_Kn_model' with current K test batch
        y_hat_K = best_Kn_model.predict(batch_x = batch_x_test)

        # Manipulate 'validation_label_folds' for the current 'Kn'.
        # We first need to concatenate all batches together with 'np.concatenate()' along the rows (axis=0)
        # Then we extract the labels and not the coordenates (remember that '_labels_folds' variables have (x_coord, y_coord, label)).
        # Since the result is of shape (N,) and the shape of 'y_hat_Kn' is (N, 1), we need to reshape (-1 indicates to take the entire lenght)
        # We convert it as integers since they originally are floats and we need the labels as indexes inside 'get_metrics()'
        y_true_K = np.concatenate(test_label_folds[K], axis = 0)[:, -1].reshape((-1,1)).astype(int)

        # Evaluate metrics by comparing the predicted labels with the true labels for the current K fold
        # Use the last column of labels since is the one containing the labels (others has coordenates)
        K_OACC = mts.get_metrics(y_true_K, y_hat_K, cm_train.numUniqueLabels)['OACC']

        if (best_K_OACC < K_OACC):
            print('\t\t Found new best model!')
            best_K_OACC = K_OACC

            # Save K CNN model
            best_K_model = best_Kn_model
            
    #*
    #* END OF OUTER DOUBLE-CROSS VALIDATION LOOP (Kn)
    #*#################################################

    # todo: Method to save CNN model in storage

print('\n\t### DOUBLE-CROSS VALIDATION IS FINISHED ###')

#*###################
#* LOAD TEST IMAGES
print("\n##########")
print("Loading test image. Please wait...")

# Create an instance of 'CubeManager'
cm_test = hsi_dm.CubeManager(patch_size = 7, batch_size = 64, dic_label = dic_label, batch_dim = batch_dim)

# Load all desired pixels to the 'CubeManager' instance 'cm_test' (all data is stored inside the instance attributes)
cm_test.load_patient_cubes(patients_list = patient_test, dir_path_gt = dir_gtMaps, dir_par_preProcessed = dir_preProImages)

print("\tTest image has been loaded. Creating test batches...")

# Create batches with the loaded data. Returns 'batches' which is a Python dictionary including 2 Python lists, 'data' and 'labels', containing all batches
batches_test = cm_test.create_batches()

print("\tTest batches have been created. Converting data batches to tensors...")

if ( batch_dim == '2D' ):
    # Convert 'data' batches to PyTorch tensors for training our Neural Network
    data_tensor_batch_test = cm_test.batch_to_tensor(batches_test['data'], data_type = torch.float)
elif ( batch_dim == '3D' ):
    # Convert 'cube' batches to PyTorch tensors for training our Neural Network
    data_tensor_batch_test = cm_test.batch_to_tensor(batches_test['cube'], data_type = torch.float)

print("\tTensors have been created.")

#*##############################################
#* PREDICT TEST IMAGES WITH OUT NEURAL NETWORK
print("\n##########")
print("Predict loaded test image with trained model.")
print("\nModel predicting patient image = ", cm_test.patients_list[0] )

if ( batch_dim == '2D' ):
    # Predict with the FourLayerNet model
    pred_labels = model.predict(batch_x = data_tensor_batch_test)
elif ( batch_dim == '3D' ):
    print(best_K_model)
    pred_labels = best_K_model.predict(batch_x = data_tensor_batch_test)

#*##############################################
#* COMPUTE METRICS WITH THE MODEL PREDICTION

if ( batch_dim == '2D' ):
    # Evaluate how well the model can predict a new image unused during training
    # batches['label4Classes']: is a Python list where each element contains the labels for each of the samples in the corresponding batch
    # by calling the 'batch_to_label_vector()' method, we generate a column numpy array from the Python list and store all batches labels in order
    # pred_labels: is a numpy column vector with all predicted labels of all batches in order
    metrics = mts.get_metrics(cm_test.batch_to_label_vector(batches_test['label4Classes']), pred_labels, cm_test.numUniqueLabels)

elif ( batch_dim == '3D' ):
    # 'batches_test['label']' contains (x_coord, y_coord, labels). We first convert this Python list to a label vector.
    # Then we need to extract all labels by using '[:, -1]'. This gives a (N,) vector, but we need to make it (N,1) to
    # compare it with the predicted labels. Also, a conversion to 'int' is needed so 'get_metrics' works properly.
    metrics = mts.get_metrics(cm_test.batch_to_label_vector(batches_test['label'])[:, -1].reshape((-1,1)).astype(int), pred_labels, cm_test.numUniqueLabels)


print("\nMetrics after predicting:")
print('\tOACC = ', str(metrics['OACC']))
print('\tACC = ', str(metrics['ACC']))
print('\tSEN = ', str(metrics['SEN']))
print('\tSPE = ', str(metrics['SPE']))
print('\tPRECISION = ', str(metrics['PRECISION']))
print('\tCONFUSION MATRIX: \n\t', str(metrics['CON_MAT']))

#*###############################
#* COMPUTE CLASSIFICATION MAP

print("\n##########")
print("Plotting classification maps")

# To compute classification maps, it is necessary to have used the 'CubeManager' class, since it
# provides the X and Y coordenates for every pixel in every predicted batch.
# Please note that 'DataManager' class does no provide the coordenates to any sample.

if ( batch_dim == '2D' ):
    # Concatenate all list elements from 'batches_test['label4Classes']' (all label batches) to a numpy array
    true_labels = cm_test.concatenate_list_to_numpy(batches_test['label4Classes'])
    # Do the same with the coordenates to know the predicted label and its corresponding position
    label_coordenates = cm_test.concatenate_list_to_numpy(batches_test['label_coords']).astype(int)

    # Extract dimension of the loaded groundTruthMap for the test patient
    dims = cm_test.patient_cubes[patient_test[0]]['raw_groundTruthMap'].shape

    # Generate classification map from the predicted labels
    mts.get_classification_map(pred_labels, true_labels, label_coordenates, dims, title="Test classification Map", plot = True, save_plot = False, save_path = None, plot_gt = False)

if ( batch_dim == '3D' ):
    # Concatenate all list elements from 'batches_test['label']' (all label batches) to a numpy array
    true_labels = cm_test.concatenate_list_to_numpy(batches_test['label'])[:, -1].reshape((-1,1)).astype(int)
    # Do the same with the coordenates to know the predicted label and its corresponding position
    label_coordenates = cm_test.concatenate_list_to_numpy(batches_test['label'])[:, 0:-1].astype(int)

    # Extract dimension of the loaded groundTruthMap for the test patient
    dims = cm_test.patient_cubes[patient_test[0]]['raw_groundTruthMap'].shape

    # Generate classification map from the predicted labels
    mts.get_classification_map(pred_labels, true_labels, label_coordenates, dims, title="Test classification Map", plot = True, save_plot = False, save_path = None, plot_gt = True)

#*#### END MAIN PROGRAM #####
#*###########################