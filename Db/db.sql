create table users(
    userID int primary key generated always as identity,
    username varchar(255) not null,
    password varchar(255) not null
);

create table broker(
    brokerID int primary key generated always as identity,
    brokerName varchar(255) not null,
    brokerLogin varchar(255) not null,
    brokerPassword varchar(255) not null,
    userID int not null,
    foreign key (userID) references users(userID)
);

create table strategy(
    strategyID int primary key generated always as identity,
    strategyName varchar(255) not null,
    created timestamp not null default current_timestamp,
    userID int not null,
    classname varchar(255) not null,
    foreign key (userID) references users(userID)
);

-- password is adminPass123

insert into users (username, password) values ('admin', '$argon2i$v=19$m=16,t=2,p=1$dGVzdF9zZWNyZXRfa2V5$9p9YiWaYDQw57iehTz57dA');