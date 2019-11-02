/*
this script is for configuring the SCIENCE_FAIR database
in other words, it creates all the tables and stuff
don't run it soon, as we haven't decided on everything

I've added OR REPLACE as a MariaDB specialty to the CREATE TABLE statements,
so that if we wanna redo things we can run this script again.
However, I'm not sure how well the constraints will hold up to my nonsense

make sure to use "-a SCIENCE_FAIR" or "USE SCIENCE_FAIR"

NOT READY TO EXECUTE
*/

CREATE OR REPLACE TABLE users
(
    ID MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
    email_addr VARCHAR(254) NOT NULL,
    username VARCHAR(100) NOT NULL,
    real_name VARCHAR(255) NOT NULL,
    time_joined TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    verified BOOLEAN NOT NULL DEFAULT 'false',
    CONSTRAINT `users_pk` PRIMARY KEY (ID)
)
ENGINE=INNODB;

CREATE OR REPLACE TABLE datasets
(
    ID MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
    title VARCHAR(255) NOT NULL,
    user_description VARCHAR(65535),
    url_sources TEXT,
    time_posted TIMESTAMP NOT NULL,
    posterID MEDIUMINT UNSIGNED NOT NULL,
    CONSTRAINT `datasets_pk` PRIMARY KEY (ID),
    CONSTRAINT `dataset_poster_fk`
        FOREIGN KEY (posterID) REFERENCES users (ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
)
ENGINE=INNODB;

CREATE OR REPLACE TABLE models
(
    ID MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
    user_description VARCHAR(65535),
    rnn_style VARCHAR(5) NOT NULL DEFAULT 'GRU',
    npl_level TINYINT NOT NULL DEFAULT 0,
    

    -- settings below are based off of the options for char-rnn
    -- signage may be incorrect, i guessed everything
    num_layers TINYINT UNSIGNED NOT NULL DEFAULT 2,
    learning_rate FLOAT UNSIGNED NOT NULL DEFAULT 0.002,
    learning_rate_decay FLOAT UNSIGNED NOT NULL DEFAULT 0.97,
    learning_rate_decay_after FLOAT UNSIGNED NOT NULL DEFAULT 10,
    dropout FLOAT NOT NULL DEFAULT 0,
    seq_length TINYINT UNSIGNED NOT NULL DEFAULT 50,
    batch_size TINYINT UNSIGNED NOT NULL DEFAULT 50,
    max_epochs TINYINT UNSIGNED NOT NULL DEFAULT 50,
    grad_clip FLOAT UNSIGNED NOT NULL DEFAULT 5,
    train_frac FLOAT UNSIGNED NOT NULL DEFAULT 0.95,
    val_frac FLOAT UNSIGNED NOT NULL DEFAULT 0.05,
    seed TINYINT NOT NULL DEFAULT 123,


    datasetID MEDIUMINT UNSIGNED NOT NULL,
    trainerID MEDIUMINT UNSIGNED NOT NULL,
    CONSTRAINT `models_pk` PRIMARY KEY (ID),
    CONSTRAINT `model_dataset_fk`
        FOREIGN KEY (datasetID) references datasets (ID)
        ON DELETE CASCADE
        ON UPDATE RESTRICT,
    CONSTRAINT 'dataset_trainer_fk'
        ON DELETE RESTRICT
        ON UPDATE CASCADE

)
ENGINE=INNODB;
/*
CREATE OR REPLACE TABLE checkpoints
ENGINE=INNODB;
*/