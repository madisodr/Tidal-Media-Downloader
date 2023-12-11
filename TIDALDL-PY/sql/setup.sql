CREATE TABLE IF NOT EXISTS `playlists` (
	`uuid` VARCHAR(255) NOT NULL,
	`title` VARCHAR(255) NOT NULL,
	`numberOfTracks` INT UNSIGNED DEFAULT 0,
    `duration` INT UNSIGNED DEFAULT 0,
	PRIMARY KEY (uuid)
);

CREATE TABLE IF NOT EXISTS  `songs` (
    `uuid` INT UNSIGNED NOT NULL AUTO_INCREMENT,
	`id` INT UNSIGNED NOT NULL,
	`title` VARCHAR(255) NOT NULL,
	`artist` VARCHAR(255) NOT NULL,
	`album` VARCHAR(255),
	`playlist` VARCHAR(255) NOT NULL,
	`duration` INT UNSIGNED DEFAULT 0,
    `trackNumberOnPlaylist` INT UNSIGNED DEFAULT 0,
	PRIMARY KEY (`uuid`),
	FOREIGN KEY (`playlist`) REFERENCES `playlists` (`uuid`)
);

