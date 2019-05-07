-- 创建数据库
create database music_recommend;
use music_recommend;

-- 创建歌单表
create table t_lists(
    list_id int unsigned default 0 primary key,
    list_link varchar(40),
    list_title varchar(80),
    list_img varchar(80),
    list_author varchar(40),
    list_amount int unsigned default 0,
    list_tags varchar(80),
    list_collection int unsigned default 0,
    list_forward int unsigned default 0,
    list_comment int unsigned default 0,
    list_description varchar(1000),
    list_songs varchar(16000) not null,
    INDEX index_listTitle(list_title)
)engine=innodb, charset utf8;

-- 创建歌曲表
create table t_songs(
    song_id int unsigned default 0 primary key,
    song_link varchar(40),
    song_name varchar(120),
    song_artist varchar(80),
    song_album varchar(200),
    song_lyric varchar(8000),
    song_comment int unsigned default 0,
    song_albumPicture varchar(80),
    song_tags varchar(80),
    INDEX index_songName(song_name),
    INDEX index_songArtist(song_artist)
)engine=innodb, charset utf8;

-- 创建用户表
create table t_users(
    user_id int unsigned auto_increment primary key,
    user_SUPER tinyint(1) default 0 not null,
    user_name varchar(100) not null unique,
    user_email varchar(30) not null unique,
    user_like varchar(200),
    user_pwd varchar(40) not null,
    INDEX index_userName(user_name)
)engine=innodb, charset utf8;

-- 创建用户行为表
create table t_actions(
    action_id int unsigned auto_increment primary key,
    action_user int unsigned not null,
    action_song int unsigned not null,
    action_like tinyint(1) default 0,
    action_unlike tinyint(1) default 0,
    action_audition tinyint(1) default 0,
    action_download tinyint(1) default 0,
    INDEX index_map(action_user, action_song),
    foreign key(action_user) references t_users(user_id),
    foreign key(action_song) references t_songs(song_id)
)engine=innodb, charset utf8;