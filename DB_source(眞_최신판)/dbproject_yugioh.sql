-- MySQL dump 10.13  Distrib 8.0.26, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: dbproject
-- ------------------------------------------------------
-- Server version	8.0.26

--
-- Table structure for table `account`
--

DROP TABLE IF EXISTS `account`;

DROP TABLE IF EXISTS belong_trap;

DROP TABLE IF EXISTS belong_magic;

DROP TABLE IF EXISTS belong_monster;

DROP TABLE IF EXISTS trap_box;
drop table if exists magic_box;
DROP TABLE IF EXISTS monster_box;

drop table if exists monster_card;
drop table if exists magic_card;
drop	table if exists trap_card;




CREATE TABLE `account` (
  `name` varchar(100) NOT NULL,
  `ID` varchar(45) NOT NULL,
  `password` varchar(45) NOT NULL,
  `gender` varchar(45) NOT NULL,
  `birth` date NOT NULL,
  `email` varchar(45) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=71 DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `account`
--

DROP TABLE IF EXISTS `apack`;
CREATE TABLE `apack` (
  `pack` varchar(100) NOT NULL,
  `series` varchar(45) NOT NULL,
  `release_year` int not null,
  `serial_number` varchar(45) not null,
  PRIMARY KEY (`pack`,`serial_number`),
  unique key (`serial_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;




--
-- Table structure for table `magic_card`
--

CREATE TABLE magic_card (
  card_name varchar(100) NOT NULL,
  icon varchar(10) DEFAULT NULL,
  join_count int NOT NULL DEFAULT 0,
  vic_count int NOT NULL DEFAULT 0,
  win_count int NOT NULL DEFAULT 0,
  lose_count int NOT NULL DEFAULT 0,
  check(icon in('일반 마법', '속공 마법', '지속 마법', '필드 마법', '장착 마법', '의식 마법' )),
  PRIMARY KEY (`card_name`)
) ENGINE=InnoDB DEFAULT  CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE magic_box (
card_name varchar(100) NOT NULL,
card_text text,
PRIMARY KEY (card_name),
constraint connect_magic foreign key(card_name) references magic_card(card_name)ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;





--
-- Table structure for table `monster_card`
--
CREATE TABLE monster_card (
  card_name varchar(100) not null,
  attribute varchar(10) NOT NULL,
  constraint mon1 check(attribute in('어둠', '빛', '땅', '물', '화염', '바람', '신')),
  card_type varchar(10) NOT NULL,
  constraint mon2 check(card_type in ('마법사족', '드래곤족', '언데드족', '전사족', '야수전사족', 
  '야수족', '비행야수족', '악마족', '천사족', '곤충족', '공룡족', '파충류족', '어류족',
'해룡족', '사이킥족', '물족', '화염족', '번개족', '암석족', '식물족', '기계족',
'환신야수족', '환룡족', '사이버스족')),
  grade_size int NOT NULL,
  type1 varchar(10) default NULL,
  type2 varchar(10) default NULL,
  constraint mon3 check(type1 in('일반', '효과',null)),
  constraint mon4 check(type2 in('융합', '의식', '싱크로', '엑시즈', '링크',null)),
  trait1 varchar(10) default NULL,
  trait2 varchar(10) default NULL,
  trait3 varchar(10) default NULL,
  constraint mon5 check(trait1 in ('스피릿', '튜너', '듀얼',null)),
  constraint mon6 check(trait2 in ('펜듈럼', '유니온', '튠',null)),
  constraint mon7 check(trait3 in ('특수소환', '리버스',null)),
  atk int NOT NULL ,
  def int DEFAULT NULL,
  constraint mon_atk check(atk<=5000),
  constraint mon_def1 check(def<=5000),
  constraint mon_def2 check(def in(null)),
  join_count int NOT NULL DEFAULT 0,
  vic_count int NOT NULL DEFAULT 0,
  win_count int NOT NULL DEFAULT 0,
  lose_count int NOT NULL DEFAULT 0,
  PRIMARY KEY (card_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;




CREATE TABLE monster_box (
card_name_box varchar(100) not null,
card_text text,
PRIMARY KEY (card_name_box),
constraint connect_monster
 foreign key (card_name_box)
 references monster_card(card_name)ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Table structure for table `trap_card`
--

CREATE TABLE trap_card (
  card_name varchar(100) NOT NULL,
  icon varchar(10) not NULL,
  check(icon in ('일반 함정', '지속 함정', '카운터 함정')),
  join_count int NOT NULL DEFAULT 0,
  vic_count int NOT NULL DEFAULT 0,
  win_count int NOT NULL DEFAULT 0,
  lose_count int NOT NULL DEFAULT 0,
  PRIMARY KEY (card_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE trap_box (
    card_name VARCHAR(100) NOT NULL,
    card_text TEXT,
    PRIMARY KEY (card_name),
   constraint connect_trap foreign key (card_name) references trap_card(card_name)ON DELETE CASCADE
)  ENGINE=INNODB DEFAULT CHARSET=UTF8MB4 COLLATE = UTF8MB4_0900_AI_CI;


--
-- Table structure for table `card_belonged`
--

CREATE TABLE belong_monster (
    serial_number VARCHAR(45) not null,
    card_number int not null,
    card_name varchar(100) not null,
    card_type VARCHAR(45) NOT NULL,
    check(card_type in ('몬스터')),
    
    
    constraint card_name_fk1	FOREIGN KEY(card_name)REFERENCES monster_card (card_name) ON DELETE CASCADE,
    
    constraint card_name_fk2	FOREIGN KEY(card_name)REFERENCES monster_box (card_name_box) ON DELETE CASCADE,
    
    
    constraint serial_number_fk FOREIGN KEY(serial_number)REFERENCES apack(serial_number)ON DELETE CASCADE,
    
    PRIMARY KEY (serial_number, card_number)
    
    
)ENGINE=INNODB DEFAULT CHARSET=UTF8MB4 COLLATE = UTF8MB4_0900_AI_CI ;


CREATE TABLE belong_magic (
    serial_number VARCHAR(45) not null,
    card_number int not null,
    card_name VARCHAR(100) NOT NULL,
    card_type VARCHAR(45) NOT NULL,
    check(card_type in ('마법')),
    PRIMARY KEY (serial_number, card_number),
    KEY card_name_idx (card_name), key serial_number_idx(serial_number),
    constraint fk_bm foreign key  (serial_number)  references apack(serial_number)ON DELETE CASCADE,
    constraint card_name3 foreign key(card_name)references magic_card(card_name)ON DELETE CASCADE,
    constraint card_name4 foreign key(card_name)references magic_box(card_name)ON DELETE CASCADE
)  ENGINE=INNODB DEFAULT CHARSET=UTF8MB4 COLLATE = UTF8MB4_0900_AI_CI;


CREATE TABLE belong_trap (
    serial_number VARCHAR(45) not null,
    card_number int not null,
    card_name VARCHAR(100) NOT NULL,
    card_type VARCHAR(45) NOT NULL,
    check(card_type in ('함정')),
    PRIMARY KEY (serial_number, card_number),
    KEY card_name_idx (card_name),key serial_number_idx(serial_number),
    constraint fk6 foreign key  (serial_number)  references apack(serial_number)ON DELETE CASCADE,
    constraint card_name5 foreign key(card_name)references trap_card(card_name)ON DELETE CASCADE,
    constraint card_name6 foreign key(card_name)references trap_box(card_name)ON DELETE CASCADE
)  ENGINE=INNODB DEFAULT CHARSET=UTF8MB4 COLLATE = UTF8MB4_0900_AI_CI;


