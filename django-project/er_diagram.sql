// Use DBML to define your database structure
// Docs: https://dbml.dbdiagram.io/docs

Table users {
  id integer [primary key]
  name varchar(100) [not null]
  email varchar(150) [unique, not null]
  password varchar(255) [not null]
  last_login timestamp [null]
  is_active boolean [default: true]
  created_at timestamp [default: 'now']
}

Table cities {
  id integer [primary key]
  name varchar(100) [not null]
}

Table hotels {
  id integer [primary key]
  name varchar(100) [not null]
  city_id integer [not null]
}


Table ads_info {
  id integer [primary key]
  image text
  rating decimal(2,1)
  price integer [not null]
  url text
  hotel_id integer
}

Table bookmarks {
  id integer [primary key]
  user_id integer
  ads_info_id integer
}

Ref hotels_cities: hotels.city_id > cities.id // many-to-one
Ref hotels_ads_info: ads_info.hotel_id > hotels.id // many-to-one
Ref bookmarks_ads_info: bookmarks.ads_info_id > ads_info.id // many-to-one
Ref bookmarks_users: bookmarks.user_id > users.id // many-to-one

