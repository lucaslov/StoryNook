import axios, { AxiosResponse } from 'axios';
import { GetMoviesResponse } from '../interfaces/GetMoviesResponse';

export async function fetchMovies(q: string = '', pSize: number = 1, pNum: number = 1): Promise<GetMoviesResponse> {
    const query = q ? `q=${q}` : '';
    const pagingParams = `&page=${pNum}&size=${pSize}`
    const response: AxiosResponse = await axios.get('http://localhost:8000/movies?' + query + pagingParams);
    const responseData: GetMoviesResponse = response.data;
    return responseData;
}

export async function checkEndpointStatus(endpoint: string): Promise<boolean> {
    try {
        const response: AxiosResponse = await axios.head(endpoint);
        return response.status >= 200 && response.status < 300;
    } catch (error) {
        return false;
    }
}