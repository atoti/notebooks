import axios from "axios";

const baseUrl = "http://localhost:8080/atoti/pyapi";

export const getLevelMembers = async (level) => {
  const url = `${baseUrl}/levels/${level}/members`;
  const response = await axios.get(url);
  return await response.data;
}

export const getWinRate = async (pokemon, opponentPokemon) => {
  const url = `${baseUrl}/measures/win-rate/${pokemon}/${opponentPokemon}`;
  const response = await axios.get(url);
  return await response.data;
}

export const addBattle = async (pokemon, opponentPokemon, winner) => {
  const url = `${baseUrl}/battle/${pokemon}/${opponentPokemon}/${winner}`;
  const response = await axios.get(url);
  return await response.data;
}
