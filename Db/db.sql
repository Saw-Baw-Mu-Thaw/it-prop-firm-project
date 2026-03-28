create table users(
    "userId" int primary key generated always as identity,
    "username" varchar(255) not null,
    "password" varchar(255) not null
);

create table broker(
    "brokerId" int primary key generated always as identity,
    "brokerName" varchar(255) not null,
    "brokerLogin" varchar(255) not null,
    "brokerPassword" varchar(255) not null,
    "userId" int not null,
    foreign key ("userId") references users("userId")
);

create table strategy(
    "strategyId" int primary key generated always as identity,
    "strategyName" varchar(255) not null,
    "created" timestamp not null default current_timestamp,
    "userId" int not null,
    "classname" varchar(255) not null,
    foreign key ("userId") references users("userId")
);

-- password is adminPass123

insert into users (username, password) values ('admin', '$argon2i$v=19$m=16,t=2,p=1$dGVzdF9zZWNyZXRfa2V5$9p9YiWaYDQw57iehTz57dA');