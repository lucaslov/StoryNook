import { LibraryMovie } from './LibraryMovie';

export interface GetMoviesResponse {
    items: LibraryMovie[];
    page: number;
    pages: number;
    size: number;
    total: number;
}
