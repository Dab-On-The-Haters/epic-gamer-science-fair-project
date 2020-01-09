/*
this script is for configuring the SCIENCE_FAIR database
in other words, it creates all the tables and stuff
don't run it soon, as we haven't decided on everything

I've added OR REPLACE as a MariaDB specialty to the CREATE TABLE statements,
so that if we wanna redo things we can run this script again.
However, I'm not sure how well the constraints will hold up to my nonsense

make sure to use "-a SCIENCE_FAIR" or "USE SCIENCE_FAIR"

ready to execute
*/


-- table of the site's users contains info like email, username, whether they've verified their email, etc..
CREATE OR REPLACE TABLE users
(
    ID MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
    email_addr VARCHAR(254) NOT NULL,
    username VARCHAR(255) NOT NULL,
    real_name VARCHAR(255) NOT NULL,
    self_description TEXT,
    own_password VARCHAR(255) NOT NULL,
    time_joined TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    verified BOOLEAN NOT NULL DEFAULT 0, -- works for is_authenticated and is_active in flask-login
    CONSTRAINT `users_pk` PRIMARY KEY (ID)
) ENGINE=InnoDB;
SHOW WARNINGS;


CREATE OR REPLACE TABLE verification_codes
(
    ID MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
    accountID MEDIUMINT UNSIGNED NOT NULL,
    codeNumber SMALLINT UNSIGNED NOT NULL,
    time_created TIMESTAMP NOT NULL,
    CONSTRAINT `account_verifying_fk`
        FOREIGN KEY (accountID) REFERENCES users (ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;
SHOW WARNINGS;


-- table of datasets that have been uploaded to the site and their info
CREATE OR REPLACE TABLE datasets
(
    ID MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
    title VARCHAR(255) NOT NULL,
    user_description TEXT,
    final_text LONGTEXT,
    time_posted TIMESTAMP NOT NULL,
    posterID MEDIUMINT UNSIGNED,
    CONSTRAINT `datasets_pk` PRIMARY KEY (ID),
    CONSTRAINT `dataset_poster_fk`
        FOREIGN KEY (posterID) REFERENCES users (ID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB;
SHOW WARNINGS;


--for files in the datasets
CREATE OR REPLACE TABLE datafiles
(
    ID MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
    file_name VARCHAR(255) NOT NULL,
    file_data LONGTEXT NOT NULL,
    datasetID MEDIUMINT UNSIGNED NOT NULL,
    CONSTRAINT `datafiles_pk` PRIMARY KEY (ID),
    CONSTRAINT `dataset_file_fk`
        FOREIGN KEY (datasetID) REFERENCES datasets (ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;
SHOW WARNINGS;


-- table of models
CREATE OR REPLACE TABLE models
(
    ID MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
    user_description TEXT,

    char_file MEDIUMBLOB,
    
    began_training TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    time_finished TIMESTAMP DEFAULT 0,
    finished_naturally BOOLEAN DEFAULT NULL,

    rnn_style VARCHAR(5) NOT NULL DEFAULT 'GRU',
    npl_level TINYINT NOT NULL DEFAULT 0,

    -- settings below are based off of the options for char-rnn
    -- signage may be incorrect, i guessed everything
    num_layers TINYINT UNSIGNED NOT NULL DEFAULT 2,
    learning_rate DOUBLE UNSIGNED NOT NULL DEFAULT 0.002,
    learning_rate_decay FLOAT UNSIGNED NOT NULL DEFAULT 0.97,
    learning_rate_decay_after SMALLINT UNSIGNED NOT NULL DEFAULT 10,
    dropout FLOAT NOT NULL DEFAULT 0.5,
    seq_length SMALLINT UNSIGNED NOT NULL DEFAULT 50,
    rnn_size SMALLINT UNSIGNED NOT NULL DEFAULT 128,
    batch_size SMALLINT UNSIGNED NOT NULL DEFAULT 50,
    max_epochs SMALLINT UNSIGNED NOT NULL DEFAULT 50,
    grad_clip FLOAT UNSIGNED NOT NULL DEFAULT 5,
    train_frac FLOAT UNSIGNED NOT NULL DEFAULT 0.95,
    val_frac FLOAT UNSIGNED NOT NULL DEFAULT 0.05,
    -- seed is for generating random numbers
    seed TINYINT NOT NULL DEFAULT 123,

    -- stuff not generated until later begins here (hopefully no nulls tho)

    -- loader.ntrain = iterations_per_epoch
    iterations_per_epoch SMALLINT UNSIGNED,
    -- iterations = loader.ntrain * epochs
    iterations MEDIUMINT UNSIGNED,

    param_amount SMALLINT UNSIGNED,
    
    pid MEDIUMINT UNSIGNED,

    datasetID MEDIUMINT UNSIGNED NOT NULL,
    trainerID MEDIUMINT UNSIGNED,
    CONSTRAINT `models_pk` PRIMARY KEY (ID),
    CONSTRAINT `model_dataset_fk`
        FOREIGN KEY (datasetID) REFERENCES datasets (ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT `dataset_trainer_fk`
        FOREIGN KEY (trainerID) REFERENCES users (ID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=INNODB;
SHOW WARNINGS;



CREATE OR REPLACE TABLE checkpoints
(
    ID BIGINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
    loss FLOAT UNSIGNED NOT NULL,
    time_saved TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    iteration MEDIUMINT UNSIGNED NOT NULL,
    epoch SMALLINT UNSIGNED NOT NULL,
    -- learning_rate FLOAT UNSIGNED NOT NULL,
    -- pytorch_data LONGBLOB NOT NULL,
    modelID MEDIUMINT UNSIGNED NOT NULL,
    final BOOLEAN NOT NULL DEFAULT 0,
    epoch_final BOOLEAN NOT NULL DEFAULT 0,
    CONSTRAINT `checkpoints_pk` PRIMARY KEY (ID),
    CONSTRAINT `model_checkpoint_fk`
        FOREIGN KEY (modelID) REFERENCES models (ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;
SHOW WARNINGS;


CREATE OR REPLACE TABLE logs
(
    ID BIGINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
    time_saved TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    loss FLOAT UNSIGNED NOT NULL,
    iteration MEDIUMINT UNSIGNED NOT NULL,
    epoch SMALLINT NOT NULL,
    -- grad_param_norm FLOAT NOT NULL,
    modelID MEDIUMINT UNSIGNED NOT NULL,
    CONSTRAINT `model_logs_fk`
        FOREIGN KEY (modelID) REFERENCES models (ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;
SHOW WARNINGS;


CREATE OR REPLACE TABLE samples
(
    ID BIGINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
    time_made TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    temperature FLOAT UNSIGNED NOT NULL DEFAULT 0.8,
    sample_length SMALLINT UNSIGNED NOT NULL DEFAULT 5000,
    seed VARCHAR(5000) NOT NULL DEFAULT "a",
    result TEXT,
    modelID MEDIUMINT UNSIGNED NOT NULL,
    checkpointID BIGINT UNSIGNED NOT NULL,
    CONSTRAINT `samples_pk` PRIMARY KEY (ID),
    CONSTRAINT `model_sample_fk`
        FOREIGN KEY (modelID) REFERENCES models (ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT `ckecpoint_sample_fk`
        FOREIGN KEY (checkpointID) REFERENCES checkpoints (ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;
SHOW WARNINGS;

CREATE OR REPLACE TABLE survey
(
    ID MEDIUMINT UNSIGNED NOT NULL,
    time_submitted = TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    tech_comfort = TINYINT UNSIGNED NOT NULL,

    navigation = TINYINT UNSIGNED NOT NULL,
    navigationF = SMALLTEXT NOT NULL,
    datasets = TINYINT UNSIGNED NOT NULL,
    datasetsF = SMALLTEXT NOT NULL,
    models = TINYINT UNSIGNED NOT NULL,
    modelsF = SMALLTEXT NOT NULL,
    samples = TINYINT UNSIGNED NOT NULL,
    samplesF = SMALLTEXT NOT NULL,
    descriptions = TINYINT UNSIGNED NOT NULL,
    descriptionsF = SMALLTEXT NOT NULL,

    generalF = SMALLTEXT NOT NULL,

    userID = MEDIUMINT UNSIGNED NOT NULL UNIQUE,
    CONSTRAINT `survey_pk` PRIMARY KEY (ID),
    CONSTRAINT `survey_author_fk`
        FOREIGN KEY (userID) REFERENCES user (ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
) ENGINE=InnoDB;
SHOW WARNINGS;
