import { LibraryMovie } from '../interfaces/LibraryMovie';

export interface ExtendedMovie extends LibraryMovie {
  currentImageSrc: string;
}